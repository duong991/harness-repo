#!/usr/bin/env node
/**
 * inspect_mongo.js - Strict read-only MongoDB inspection utility.
 * Resolves the `mongodb` driver from the consumer workspace named by config
 * `nodeResolveFrom` (via module.createRequire), never from a bundled copy.
 * Every operation is checked by mongo_guard.js before it reaches the driver.
 */
'use strict';

const { loadRuntimeContext, resolveFromWorkspace, EnvFileRefused, ConfigError, ProdGateError } = require('./config');
const { validateMongoOperation } = require('./mongo_guard');
const { redactSensitive } = require('./redact');
const { prepareQuery, idLikeStringFields, toEvidence, EjsonError } = require('./mongo_ejson');

function printUsage(defaultDb) {
  console.log(`Usage: node inspect_mongo.js [options]
Options:
  --env <name>            Environment from config (default: first non-production)
  --root <path>            Repository root override (default: nearest ancestor with .git)
  --confirm-prod           Required together with --env <prod> to use a production environment
  --db <name>              Target database (default: first db in the selected environment's mongo.dbs${defaultDb ? `, e.g. '${defaultDb}'` : ''})
  --collection <name>      Target collection to inspect
  --filter <json>          JSON filter (e.g. '{"userId": {"$oid": "65f1..."}}'). Use Extended JSON
                           {"$oid": "<hex>"} / {"$date": "<ISO>"} for typed values; a 24-hex
                           string under _id is converted automatically, other fields never are
  --limit <n>              Maximum documents to return (default: 5, max: 50)
  --count                  Count matching documents (countDocuments)
  --distinct <field>       Return distinct values of a field (distinct)
  --pipeline <json>        Read-only aggregation pipeline (aggregate); same $oid/$date rules;
                           rejects $out/$merge at any depth
  --list-collections       List all collections in target database
  --list-dbs               List all databases on the MongoDB cluster
  -h, --help               Show this help

Strict read-only: only find / countDocuments / distinct / aggregate reach the driver,
and aggregate pipelines containing $out or $merge (at any nesting depth) are rejected.`);
}

function parseJsonArg(name, value) {
  try {
    return JSON.parse(value);
  } catch (err) {
    console.error(`ERROR parsing --${name} JSON: ${err.message}`);
    process.exit(1);
  }
}

function prepareArg(name, value, ObjectId) {
  try {
    return prepareQuery(parseJsonArg(name, value), ObjectId);
  } catch (err) {
    if (err instanceof EjsonError) {
      console.error(`ERROR in --${name}: ${err.message}`);
      process.exit(1);
    }
    throw err;
  }
}

function emptyResultHint(filter) {
  const fields = idLikeStringFields(filter);
  if (!fields.length) return undefined;
  return `0 matches. Field(s) ${fields.join(', ')} were queried as plain strings; if they are stored as ` +
    `ObjectId, re-run with {"<field>": {"$oid": "<hex>"}}. A string-vs-ObjectId difference is evidence to ` +
    `report, not something to fix in this skill or in application code.`;
}

async function main() {
  const args = process.argv.slice(2);
  let dbName = null;
  let collectionName = '';
  let filterStr = '{}';
  let pipelineStr = null;
  let distinctField = null;
  let limit = 5;
  let isCount = false;
  let isListCollections = false;
  let isListDbs = false;

  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--db' && args[i + 1]) dbName = args[++i];
    else if (a === '--collection' && args[i + 1]) collectionName = args[++i];
    else if (a === '--filter' && args[i + 1]) filterStr = args[++i];
    else if (a === '--pipeline' && args[i + 1]) pipelineStr = args[++i];
    else if (a === '--distinct' && args[i + 1]) distinctField = args[++i];
    else if (a === '--limit' && args[i + 1]) limit = Math.min(50, Math.max(1, parseInt(args[++i], 10) || 5));
    else if (a === '--count') isCount = true;
    else if (a === '--list-collections') isListCollections = true;
    else if (a === '--list-dbs') isListDbs = true;
    else if (a === '--help' || a === '-h') {
      printUsage();
      process.exit(0);
    }
    // --env/--root/--confirm-prod are consumed by loadRuntimeContext()
  }

  let ctx;
  try {
    ctx = loadRuntimeContext();
  } catch (err) {
    if (err instanceof EnvFileRefused || err instanceof ConfigError || err instanceof ProdGateError) {
      console.error(`ERROR: ${err.message}`);
      process.exit(err instanceof ProdGateError ? 3 : err instanceof EnvFileRefused ? 4 : 2);
    }
    throw err;
  }

  if (!dbName) dbName = ctx.mongoDbs[0];
  if (!dbName) {
    console.error('ERROR: --db is required (no mongo.dbs configured for this environment)');
    process.exit(1);
  }

  let MongoClient, ObjectId;
  try {
    ({ MongoClient, ObjectId } = resolveFromWorkspace(ctx.repoRoot, ctx.nodeResolveFrom, 'mongodb'));
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(2);
  }

  function sanitizeUri(uriStr) {
    return (uriStr || '').replace(/\/\/[^:]+:[^@]+@/, '//***:***@');
  }

  let uri = ctx.mongoUri;
  if (ctx.mongoUser && ctx.mongoPass && !uri.includes('@')) {
    uri = uri.replace(/^mongodb(?:\+srv)?:\/\//, (m) => `${m}${encodeURIComponent(ctx.mongoUser)}:${encodeURIComponent(ctx.mongoPass)}@`);
  }

  const client = new MongoClient(uri, { serverSelectionTimeoutMS: 5000 });

  try {
    await client.connect();

    if (isListDbs) {
      const dbs = await client.db('admin').admin().listDatabases();
      console.log(JSON.stringify({
        cluster: sanitizeUri(uri),
        databases: dbs.databases.map((d) => ({ name: d.name, sizeOnDisk: d.sizeOnDisk, empty: d.empty })),
      }, null, 2));
      return;
    }

    const db = client.db(dbName);

    if (isListCollections) {
      const collections = await db.listCollections().toArray();
      console.log(JSON.stringify({ database: dbName, collections: collections.map((c) => c.name) }, null, 2));
      return;
    }

    if (!collectionName) {
      console.error('ERROR: --collection <name> is required (or use --list-collections, --list-dbs)');
      process.exit(1);
    }
    const collection = db.collection(collectionName);

    if (pipelineStr !== null) {
      const pipeline = prepareArg('pipeline', pipelineStr, ObjectId);
      validateMongoOperation('aggregate', { pipeline });
      const docs = await collection.aggregate(pipeline, { allowDiskUse: false }).limit(limit).toArray();
      console.log(JSON.stringify({
        database: dbName,
        collection: collectionName,
        pipeline: toEvidence(pipeline),
        returned: docs.length,
        hint: docs.length ? undefined : emptyResultHint(pipeline),
        documents: redactSensitive(toEvidence(docs), ctx.redactionFields),
      }, null, 2));
      return;
    }

    if (distinctField) {
      validateMongoOperation('distinct');
      const filter = prepareArg('filter', filterStr, ObjectId);
      const values = await collection.distinct(distinctField, filter);
      console.log(JSON.stringify({ database: dbName, collection: collectionName, field: distinctField, filter: toEvidence(filter), values: redactSensitive(toEvidence(values), ctx.redactionFields) }, null, 2));
      return;
    }

    const filter = prepareArg('filter', filterStr, ObjectId);

    if (isCount) {
      validateMongoOperation('countDocuments');
      const count = await collection.countDocuments(filter);
      console.log(JSON.stringify({
        database: dbName,
        collection: collectionName,
        filter: toEvidence(filter),
        count,
        hint: count ? undefined : emptyResultHint(filter),
      }, null, 2));
    } else {
      validateMongoOperation('find');
      const docs = await collection.find(filter).limit(limit).toArray();
      console.log(JSON.stringify({
        database: dbName,
        collection: collectionName,
        filter: toEvidence(filter),
        returned: docs.length,
        hint: docs.length ? undefined : emptyResultHint(filter),
        documents: redactSensitive(toEvidence(docs), ctx.redactionFields),
      }, null, 2));
    }
  } catch (err) {
    console.error(`ERROR querying MongoDB (${sanitizeUri(uri)}/${dbName}): ${err.message}`);
    process.exit(2);
  } finally {
    await client.close();
  }
}

main();
