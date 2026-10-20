#!/usr/bin/env node
/**
 * trace_kafka.js - Strict read-only Kafka topic/offset/message inspector.
 * Resolves `kafkajs` from the consumer workspace named by config
 * `nodeResolveFrom` (via module.createRequire). Uses an ephemeral probe
 * consumer group and never commits offsets or produces messages
 * (see tools/kafka_guard.js).
 */
'use strict';

const { loadRuntimeContext, resolveFromWorkspace, EnvFileRefused, ConfigError, ProdGateError } = require('./config');
const { buildReadOnlyRunConfig, ephemeralGroupId } = require('./kafka_guard');
const { redactSensitive } = require('./redact');

function printUsage() {
  console.log(`Usage: node trace_kafka.js [options]
Options:
  --env <name>            Environment from config (default: first non-production)
  --root <path>            Repository root override (default: nearest ancestor with .git)
  --confirm-prod           Required together with --env <prod> to use a production environment
  --brokers <list>         Comma-separated Kafka brokers (default: environment config/credentials)
  --client-id <id>         Explicit client ID (default: kafkaClientId from credentials/config)
  --topic <name>           Topic to inspect
  --limit <n>              Maximum messages to peek (default: 10, max: 50)
  --list-topics            List all topics on cluster
  --offsets                Fetch partitions and latest offsets for topic
  --from-beginning         Read messages from the beginning instead of latest
  -h, --help               Show this help

Strict read-only: uses an ephemeral probe consumer group, autoCommit is always
false, and this tool never calls commitOffsets or produce/send.`);
}

async function main() {
  const args = process.argv.slice(2);
  let brokersOverride = null;
  let clientIdOverride = null;
  let topic = '';
  let limit = 10;
  let isListTopics = false;
  let isOffsets = false;
  let fromBeginning = false;

  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--brokers' && args[i + 1]) brokersOverride = args[++i];
    else if (a === '--client-id' && args[i + 1]) clientIdOverride = args[++i];
    else if ((a === '--topic' || a === '-t') && args[i + 1]) topic = args[++i];
    else if (a === '--limit' && args[i + 1]) limit = Math.min(50, Math.max(1, parseInt(args[++i], 10) || 10));
    else if (a === '--list-topics') isListTopics = true;
    else if (a === '--offsets') isOffsets = true;
    else if (a === '--from-beginning') fromBeginning = true;
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

  let Kafka;
  try {
    ({ Kafka } = resolveFromWorkspace(ctx.repoRoot, ctx.nodeResolveFrom, 'kafkajs'));
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(2);
  }

  const brokersStr = brokersOverride || ctx.kafkaBrokers;
  const clientId = clientIdOverride || ctx.kafkaClientId;
  const brokers = brokersStr.split(',').map((b) => b.trim()).filter(Boolean);

  const kafka = new Kafka({ clientId, brokers, connectionTimeout: 5000, requestTimeout: 10000 });
  const admin = kafka.admin();

  try {
    await admin.connect();

    if (isListTopics) {
      const topics = await admin.listTopics();
      console.log(JSON.stringify({ brokers, clientId, count: topics.length, topics }, null, 2));
      return;
    }

    if (!topic) {
      console.error('ERROR: --topic <name> is required (or use --list-topics)');
      process.exit(1);
    }

    if (isOffsets) {
      const offsets = await admin.fetchTopicOffsets(topic);
      console.log(JSON.stringify({ brokers, clientId, topic, partitions: offsets }, null, 2));
      return;
    }

    // Ephemeral read-only consumer probe. autoCommit is enforced false by
    // buildReadOnlyRunConfig(); this code path never calls commitOffsets or
    // produce/send.
    const probeGroupId = ephemeralGroupId(clientId);
    const consumer = kafka.consumer({ groupId: probeGroupId, sessionTimeout: 10000 });

    await consumer.connect();
    await consumer.subscribe({ topic, fromBeginning });

    const messages = [];
    const timeoutPromise = new Promise((resolve) => setTimeout(resolve, 5000));

    const runPromise = consumer.run(buildReadOnlyRunConfig({
      autoCommit: false,
      eachMessage: async ({ partition, message }) => {
        messages.push({
          partition,
          offset: message.offset,
          timestamp: message.timestamp ? new Date(parseInt(message.timestamp, 10)).toISOString() : null,
          key: message.key ? message.key.toString('utf8') : null,
          value: redactSensitive(message.value ? message.value.toString('utf8') : null, ctx.redactionFields),
          headers: message.headers
            ? Object.fromEntries(Object.entries(message.headers).map(([k, v]) => [k, v ? v.toString('utf8') : null]))
            : {},
        });
        if (messages.length >= limit) {
          await consumer.stop();
        }
      },
    }));

    await Promise.race([runPromise, timeoutPromise]);
    try { await consumer.disconnect(); } catch (_) { /* best-effort */ }

    console.log(JSON.stringify({ topic, clientId, probeGroupId, messagesReturned: messages.length, messages }, null, 2));
  } catch (err) {
    console.error(`ERROR connecting to Kafka brokers (${brokersStr}) with clientId '${clientId}': ${err.message}`);
    process.exit(2);
  } finally {
    try { await admin.disconnect(); } catch (_) { /* best-effort */ }
  }
}

main();
