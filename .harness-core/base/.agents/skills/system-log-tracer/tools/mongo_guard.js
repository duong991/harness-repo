#!/usr/bin/env node
/**
 * mongo_guard.js - Pure read-only guard for MongoDB operations. Importable
 * WITHOUT the `mongodb` driver so tests can exercise it even when the driver
 * is not installed anywhere resolvable.
 */
'use strict';

const ALLOWED_OPERATIONS = new Set(['find', 'countDocuments', 'distinct', 'aggregate']);

// Aggregation (and any nested $facet/$unionWith sub-pipeline) stage names
// that perform a write. Checked recursively at any nesting depth.
const FORBIDDEN_STAGES = new Set(['$out', '$merge']);

class MongoWriteRejected extends Error {}

/**
 * Recursively scan an aggregation pipeline (array of stage objects) or any
 * nested structure for forbidden write stages, including inside $facet
 * sub-pipelines, $unionWith, $lookup pipelines, etc.
 */
function findForbiddenStage(node) {
  if (Array.isArray(node)) {
    for (const item of node) {
      const hit = findForbiddenStage(item);
      if (hit) return hit;
    }
    return null;
  }
  if (node && typeof node === 'object') {
    for (const key of Object.keys(node)) {
      if (FORBIDDEN_STAGES.has(key)) return key;
      const hit = findForbiddenStage(node[key]);
      if (hit) return hit;
    }
  }
  return null;
}

/**
 * Validate a requested Mongo operation before it is ever sent to the driver.
 * Throws MongoWriteRejected for anything outside the read-only allow-list, or
 * an aggregate pipeline containing $out/$merge at any depth.
 */
function validateMongoOperation(operationName, options) {
  options = options || {};
  if (!ALLOWED_OPERATIONS.has(operationName)) {
    throw new MongoWriteRejected(
      `MongoDB operation '${operationName}' is BLOCKED. This tool is strictly read-only. ` +
      `Permitted operations: ${Array.from(ALLOWED_OPERATIONS).sort().join(', ')}`
    );
  }
  if (operationName === 'aggregate') {
    const pipeline = options.pipeline || [];
    const stage = findForbiddenStage(pipeline);
    if (stage) {
      throw new MongoWriteRejected(
        `Aggregation stage '${stage}' is a write operation and is BLOCKED in this read-only skill.`
      );
    }
  }
  return true;
}

module.exports = { validateMongoOperation, findForbiddenStage, ALLOWED_OPERATIONS, FORBIDDEN_STAGES, MongoWriteRejected };
