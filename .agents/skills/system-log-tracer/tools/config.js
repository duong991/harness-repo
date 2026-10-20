#!/usr/bin/env node
/**
 * config.js - Shared config/credential loader for the Node tools
 * (inspect_mongo.js, trace_kafka.js). Mirrors tools/common.py: no third-party
 * dependencies, no jsonschema package, reads the same
 * `<repo-root>/.agents/config/system-log-tracer.json`.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

function skillDir() {
  return path.resolve(__dirname, '..');
}

function findRepoRoot(start) {
  const override = process.env.SLT_ROOT;
  if (override) return path.resolve(override);
  let cur = path.resolve(start || process.cwd());
  while (true) {
    if (fs.existsSync(path.join(cur, '.git'))) return cur;
    const parent = path.dirname(cur);
    if (parent === cur) return path.resolve(start || process.cwd());
    cur = parent;
  }
}

function envLikeFiles(dir) {
  if (!dir || !fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) return [];
  const out = [];
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    if (!fs.statSync(full).isFile()) continue;
    if (name === '.env' || (name.startsWith('system-log-tracer') && name.endsWith('.env'))) {
      out.push(full);
    }
  }
  return out;
}

class EnvFileRefused extends Error {}
class ConfigError extends Error {}
class ProdGateError extends Error {}

function refuseIfEnvFilesPresent(repoRoot) {
  const violations = [
    ...envLikeFiles(skillDir()),
    ...envLikeFiles(path.join(repoRoot, '.agents', 'config')),
  ];
  if (violations.length) {
    throw new EnvFileRefused(
      'Refusing to run: found .env file(s) in a location this skill treats as ' +
      'in-repository secret leakage risk: ' + violations.join(', ') +
      '. Store credentials at ~/.config/system-log-tracer/<env>.env (mode 600) instead.'
    );
  }
}

// --- minimal JSON-Schema-subset validator (mirrors common.py validate_schema) ---
function validateSchema(instance, schema, p) {
  p = p || '$';
  const errors = [];
  const t = schema.type;
  if (t) {
    const checks = {
      object: instance !== null && typeof instance === 'object' && !Array.isArray(instance),
      array: Array.isArray(instance),
      string: typeof instance === 'string',
      boolean: typeof instance === 'boolean',
      number: typeof instance === 'number',
    };
    if (t in checks && !checks[t]) {
      errors.push(`${p}: expected type '${t}', got '${typeof instance}'`);
      return errors;
    }
  }
  if (t === 'object' && instance && typeof instance === 'object') {
    for (const req of schema.required || []) {
      if (!(req in instance)) errors.push(`${p}: missing required property '${req}'`);
    }
    const props = schema.properties || {};
    const additional = 'additionalProperties' in schema ? schema.additionalProperties : true;
    for (const key of Object.keys(instance)) {
      if (key in props) {
        errors.push(...validateSchema(instance[key], props[key], `${p}.${key}`));
      } else if (additional && typeof additional === 'object') {
        errors.push(...validateSchema(instance[key], additional, `${p}.${key}`));
      } else if (additional === false) {
        errors.push(`${p}: unexpected property '${key}'`);
      }
    }
  }
  if (t === 'array' && Array.isArray(instance)) {
    if (schema.minItems !== undefined && instance.length < schema.minItems) {
      errors.push(`${p}: expected at least ${schema.minItems} item(s)`);
    }
    if (schema.items) {
      instance.forEach((item, i) => errors.push(...validateSchema(item, schema.items, `${p}[${i}]`)));
    }
  }
  if (schema.enum && !schema.enum.includes(instance)) {
    errors.push(`${p}: value ${JSON.stringify(instance)} is not one of ${JSON.stringify(schema.enum)}`);
  }
  return errors;
}

function configPath(repoRoot) {
  return path.join(repoRoot, '.agents', 'config', 'system-log-tracer.json');
}

function loadConfig(repoRoot) {
  const p = configPath(repoRoot);
  if (!fs.existsSync(p)) {
    throw new ConfigError(
      `Config not found at ${p}. Copy ${path.join(skillDir(), 'config.example.json')} ` +
      'there and edit it for your environments, services, and nodeResolveFrom.'
    );
  }
  let data;
  try {
    data = JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (err) {
    throw new ConfigError(`Config at ${p} is not valid JSON: ${err.message}`);
  }
  const schema = JSON.parse(fs.readFileSync(path.join(skillDir(), 'config.schema.json'), 'utf8'));
  const errors = validateSchema(data, schema);
  const envs = data && data.environments;
  if (envs && typeof envs === 'object') {
    const hasNonProd = Object.values(envs).some((v) => v && !v.isProduction);
    if (!hasNonProd) errors.push('$.environments: at least one environment must have isProduction=false');
  }
  if (errors.length) {
    throw new ConfigError(`Config at ${p} failed validation:\n  - ${errors.join('\n  - ')}`);
  }
  return data;
}

function credentialsDir() {
  return process.env.SLT_CREDENTIALS_DIR || path.join(os.homedir(), '.config', 'system-log-tracer');
}

function credentialsPath(envName) {
  return path.join(credentialsDir(), `${envName}.env`);
}

function parseEnvText(text) {
  const out = {};
  for (const rawLine of text.split('\n')) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#') || !line.includes('=')) continue;
    const idx = line.indexOf('=');
    const k = line.slice(0, idx).trim();
    const v = line.slice(idx + 1).trim().replace(/^['"]|['"]$/g, '');
    out[k] = v;
  }
  return out;
}

function checkCredentialFileMode(p) {
  try {
    const mode = fs.statSync(p).mode & 0o777;
    return (mode & 0o077) ? mode : null;
  } catch (_) {
    return null;
  }
}

function loadCredentials(envName) {
  const p = credentialsPath(envName);
  if (!fs.existsSync(p)) return {};
  const badMode = checkCredentialFileMode(p);
  if (badMode !== null) {
    console.error(`WARNING: credential file ${p} has mode ${(badMode & 0o777).toString(8)}; expected 600 or stricter.`);
  }
  return parseEnvText(fs.readFileSync(p, 'utf8'));
}

function selectEnvironment(config, requestedEnv, confirmProd) {
  const envs = config.environments || {};
  if (!Object.keys(envs).length) throw new ConfigError('Config has no environments defined.');

  let envName = requestedEnv;
  if (!envName) {
    envName = Object.keys(envs).find((name) => !envs[name].isProduction);
    if (!envName) throw new ConfigError('Config defines only production environments; pass --env explicitly.');
  }
  if (!(envName in envs)) {
    throw new ConfigError(`Unknown environment '${envName}'. Known: ${Object.keys(envs).join(', ')}`);
  }
  const spec = envs[envName];
  const isProd = !!spec.isProduction;
  if (isProd) {
    if (!confirmProd) {
      throw new ProdGateError(
        `Environment '${envName}' is production. Refusing without --confirm-prod. ` +
        `Ask the user for explicit chat confirmation before re-running with --env ${envName} --confirm-prod.`
      );
    }
    const credPath = credentialsPath(envName);
    if (!fs.existsSync(credPath)) {
      throw new ProdGateError(
        `Environment '${envName}' is production and also requires the credential file ` +
        `${credPath} to exist, in addition to --confirm-prod. Refusing.`
      );
    }
  }
  const creds = loadCredentials(envName);
  return { envName, spec, creds, isProd };
}

function parseCommonFlags(argv) {
  const args = argv || process.argv.slice(2);
  const out = { env: null, root: null, confirmProd: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--env' && args[i + 1]) out.env = args[++i];
    else if (args[i] === '--root' && args[i + 1]) out.root = args[++i];
    else if (args[i] === '--confirm-prod') out.confirmProd = true;
  }
  return out;
}

function loadRuntimeContext(opts) {
  opts = opts || {};
  const flags = parseCommonFlags(opts.argv);
  const env = opts.env !== undefined ? opts.env : flags.env;
  const root = opts.root !== undefined ? opts.root : flags.root;
  const confirmProd = opts.confirmProd !== undefined ? opts.confirmProd : flags.confirmProd;

  const repoRoot = findRepoRoot(root);
  refuseIfEnvFilesPresent(repoRoot);
  const config = loadConfig(repoRoot);
  const { envName, spec, creds, isProd } = selectEnvironment(config, env, confirmProd);

  function pick(key, def) {
    if (creds[key] !== undefined) return creds[key];
    if (process.env[key] !== undefined) return process.env[key];
    return def;
  }

  return {
    repoRoot,
    envName,
    isProduction: isProd,
    config,
    nodeResolveFrom: config.nodeResolveFrom,
    redactionFields: config.redactionFields || [],
    mongoDbs: (spec.mongo && spec.mongo.dbs) || [],
    mongoUri: pick('MONGO_URI', 'mongodb://127.0.0.1:27017'),
    mongoUser: pick('MONGO_USER', ''),
    mongoPass: pick('MONGO_PASSWORD', ''),
    kafkaBrokers: pick('KAFKA_BROKERS', ((spec.kafka && spec.kafka.brokers) || ['localhost:9092']).join(',')),
    kafkaClientId: pick('KAFKA_CLIENT_ID', 'system-log-tracer'),
  };
}

function resolveFromWorkspace(repoRoot, nodeResolveFrom, moduleName) {
  if (!nodeResolveFrom) {
    throw new ConfigError(
      "Config is missing 'nodeResolveFrom' (e.g. 'apps/example-service'); " +
      `cannot resolve '${moduleName}'.`
    );
  }
  const pkgJsonPath = path.join(repoRoot, nodeResolveFrom, 'package.json');
  if (!fs.existsSync(pkgJsonPath)) {
    throw new ConfigError(
      `nodeResolveFrom '${nodeResolveFrom}' does not contain a package.json at ` +
      `${pkgJsonPath}; cannot resolve '${moduleName}'. Point nodeResolveFrom at a ` +
      'workspace package that depends on it.'
    );
  }
  const require2 = require('module').createRequire(pkgJsonPath);
  try {
    return require2(moduleName);
  } catch (err) {
    throw new ConfigError(
      `Could not resolve '${moduleName}' from workspace '${nodeResolveFrom}' ` +
      `(${pkgJsonPath}): ${err.message}. Install it in that workspace, or point ` +
      "nodeResolveFrom at a workspace that does."
    );
  }
}

// ---------------------------------------------------------------------------
// Skill integrity (Harness baseline hashes). Mirrors verify_skill_integrity in
// common.py: every skill file must match .harness-core/manifest.json, derived
// from this file's own location (never SLT_ROOT), before any tool runs.
// ---------------------------------------------------------------------------

class IntegrityError extends Error {}

const EXIT_INTEGRITY = 5;

function findHarnessRoot(start) {
  let cur = path.resolve(start);
  while (true) {
    if (fs.existsSync(path.join(cur, '.harness-core', 'manifest.json'))) return cur;
    const parent = path.dirname(cur);
    if (parent === cur) return null;
    cur = parent;
  }
}

function listSkillFiles(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === '__pycache__') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...listSkillFiles(full));
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

function verifySkillIntegrity(skill, harnessRoot) {
  skill = fs.realpathSync(skill || skillDir());
  harnessRoot = harnessRoot ? fs.realpathSync(harnessRoot) : findHarnessRoot(skill);
  if (!harnessRoot) {
    throw new IntegrityError(
      `No .harness-core/manifest.json found above ${skill}; this skill only runs as a Harness-managed install.`
    );
  }
  const manifest = JSON.parse(fs.readFileSync(path.join(harnessRoot, '.harness-core', 'manifest.json'), 'utf8'));
  const prefix = path.relative(harnessRoot, skill).split(path.sep).join('/') + '/';
  const expected = new Map();
  for (const e of manifest.files || []) {
    if (e && typeof e.path === 'string' && e.path.startsWith(prefix)) expected.set(e.path, e.upstream_sha256);
  }
  const problems = [];
  const seen = new Set();
  for (const f of listSkillFiles(skill).sort()) {
    const rel = path.relative(harnessRoot, f).split(path.sep).join('/');
    seen.add(rel);
    const digest = crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
    if (!expected.has(rel)) problems.push(`unmanaged file ${rel}`);
    else if (expected.get(rel) !== digest) problems.push(`modified ${rel}`);
  }
  for (const rel of [...expected.keys()].sort()) if (!seen.has(rel)) problems.push(`missing ${rel}`);
  if (problems.length) {
    throw new IntegrityError(
      'Refusing to run: system-log-tracer files differ from the Harness baseline (' + problems.join('; ') +
      '). Do not edit skill files to get past a guard; report the blocked operation to the user. ' +
      'Legitimate changes go through the Harness update workflow (base snapshot + manifest hash).'
    );
  }
}

module.exports = {
  verifySkillIntegrity,
  findHarnessRoot,
  IntegrityError,
  EXIT_INTEGRITY,
  skillDir,
  findRepoRoot,
  refuseIfEnvFilesPresent,
  validateSchema,
  configPath,
  loadConfig,
  credentialsDir,
  credentialsPath,
  parseEnvText,
  checkCredentialFileMode,
  loadCredentials,
  selectEnvironment,
  parseCommonFlags,
  loadRuntimeContext,
  resolveFromWorkspace,
  EnvFileRefused,
  ConfigError,
  ProdGateError,
};

// Enforced on load so every Node tool that requires this module is covered.
// There is deliberately no bypass flag or environment variable.
try {
  verifySkillIntegrity();
} catch (err) {
  if (err instanceof IntegrityError) {
    console.error(`ERROR: ${err.message}`);
    process.exit(EXIT_INTEGRITY);
  }
  throw err;
}
