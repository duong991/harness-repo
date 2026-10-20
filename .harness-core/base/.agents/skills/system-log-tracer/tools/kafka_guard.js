#!/usr/bin/env node
/**
 * kafka_guard.js - Pure read-only guard for Kafka consumer configuration.
 * Importable WITHOUT the `kafkajs` driver. trace_kafka.js must build its
 * consumer `run()` config through `buildReadOnlyRunConfig()` so the ephemeral
 * group never auto-commits and the tool never calls commitOffsets/produce.
 */
'use strict';

class KafkaWriteRejected extends Error {}

/**
 * Validate (and return, unmodified) a `consumer.run({...})` config, refusing
 * anything that is not explicitly read-only.
 */
function buildReadOnlyRunConfig(runConfig) {
  runConfig = runConfig || {};
  if (runConfig.autoCommit !== false) {
    throw new KafkaWriteRejected(
      "Kafka consumer run config must set autoCommit: false explicitly; " +
      "this read-only skill never commits offsets."
    );
  }
  return runConfig;
}

/** Ephemeral, per-run consumer group id so no durable group state is created. */
function ephemeralGroupId(clientId) {
  return `${clientId}-trace-probe-${Date.now()}`;
}

// Method names that must never appear as a call on a Kafka client object in
// this tool's source. Used by the offline self-check test (string scan, not
// a live connection) to prove no write path exists.
const FORBIDDEN_CALL_PATTERNS = [
  /\.commitOffsets\s*\(/,
  /\.produce\s*\(/,
  /kafka\.producer\s*\(/,
  /\.send\s*\(\s*\{\s*topic/,
];

function assertSourceHasNoWriteCalls(sourceText) {
  for (const pattern of FORBIDDEN_CALL_PATTERNS) {
    if (pattern.test(sourceText)) {
      throw new KafkaWriteRejected(`Forbidden write-capable call pattern found: ${pattern}`);
    }
  }
  return true;
}

module.exports = {
  buildReadOnlyRunConfig,
  ephemeralGroupId,
  assertSourceHasNoWriteCalls,
  FORBIDDEN_CALL_PATTERNS,
  KafkaWriteRejected,
};
