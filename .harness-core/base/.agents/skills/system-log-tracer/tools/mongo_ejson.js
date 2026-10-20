#!/usr/bin/env node
/**
 * mongo_ejson.js - Pure MongoDB type handling for inspect_mongo.js. Importable
 * WITHOUT the `mongodb` driver: callers pass the driver's ObjectId class in.
 *
 * Input (filters and pipelines):
 *   - Explicit MongoDB Extended JSON `{"$oid": "<24 hex>"}` and
 *     `{"$date": "<ISO 8601>"}` are converted at any depth.
 *   - A plain 24-hex string is converted to ObjectId only when it is the value
 *     of an `_id` key, directly or inside `$eq`/`$ne`/`$in`/`$nin`. Other
 *     fields are never guessed: a reference may legitimately be stored as a
 *     string, and silently retyping it would change the evidence.
 *
 * Output (evidence):
 *   - ObjectId -> {"$oid": hex}, Date -> {"$date": ISO}, other BSON values ->
 *     {"$<type>": string}. Types stay visible, so a string-vs-ObjectId
 *     mismatch is reported as evidence instead of being hidden.
 */
'use strict';

const HEX24 = /^[0-9a-fA-F]{24}$/;
const ID_OPERATORS = new Set(['$eq', '$ne', '$in', '$nin']);

class EjsonError extends Error {}

function isPlainObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v) && Object.getPrototypeOf(v) === Object.prototype;
}

function makeObjectId(ObjectId, hex) {
  if (!HEX24.test(hex)) throw new EjsonError(`Invalid ObjectId '${hex}': expected 24 hexadecimal characters`);
  return new ObjectId(hex);
}

/** Convert explicit {"$oid"} / {"$date"} wrappers anywhere in a parsed JSON value. */
function fromExtendedJson(value, ObjectId) {
  if (Array.isArray(value)) return value.map((v) => fromExtendedJson(v, ObjectId));
  if (!isPlainObject(value)) return value;
  const keys = Object.keys(value);
  if (keys.length === 1 && keys[0] === '$oid') {
    if (typeof value.$oid !== 'string') throw new EjsonError('$oid must be a string');
    return makeObjectId(ObjectId, value.$oid);
  }
  if (keys.length === 1 && keys[0] === '$date') {
    const d = new Date(value.$date);
    if (Number.isNaN(d.getTime())) throw new EjsonError(`Invalid $date '${value.$date}'`);
    return d;
  }
  const out = {};
  for (const k of keys) out[k] = fromExtendedJson(value[k], ObjectId);
  return out;
}

function coerceIdValue(value, ObjectId) {
  if (typeof value === 'string' && HEX24.test(value)) return makeObjectId(ObjectId, value);
  if (Array.isArray(value)) return value.map((v) => coerceIdValue(v, ObjectId));
  if (isPlainObject(value)) {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = ID_OPERATORS.has(k) ? coerceIdValue(v, ObjectId) : v;
    return out;
  }
  return value;
}

/** Coerce 24-hex strings under `_id` keys (at any depth, e.g. inside $or/$match). */
function coerceIdFields(value, ObjectId) {
  if (Array.isArray(value)) return value.map((v) => coerceIdFields(v, ObjectId));
  if (!isPlainObject(value)) return value;
  const out = {};
  for (const [k, v] of Object.entries(value)) {
    out[k] = k === '_id' ? coerceIdValue(v, ObjectId) : coerceIdFields(v, ObjectId);
  }
  return out;
}

/** Full input preparation for a --filter or --pipeline value. */
function prepareQuery(parsed, ObjectId) {
  return coerceIdFields(fromExtendedJson(parsed, ObjectId), ObjectId);
}

/** Non-_id field paths whose value is a plain 24-hex string (hint candidates). */
function idLikeStringFields(value, prefix) {
  const found = [];
  const walk = (v, path) => {
    if (typeof v === 'string' && HEX24.test(v) && !/(^|\.)_id$/.test(path)) found.push(path);
    else if (Array.isArray(v)) v.forEach((item) => walk(item, path));
    else if (isPlainObject(v)) {
      for (const [k, child] of Object.entries(v)) walk(child, k.startsWith('$') ? path : (path ? `${path}.${k}` : k));
    }
  };
  walk(value, prefix || '');
  return Array.from(new Set(found.filter(Boolean)));
}

function bsonType(v) {
  return v && typeof v === 'object' && typeof v._bsontype === 'string' ? v._bsontype : null;
}

/** Convert driver results into type-preserving, JSON-safe evidence. */
function toEvidence(value) {
  if (value instanceof Date) return { $date: Number.isNaN(value.getTime()) ? 'Invalid Date' : value.toISOString() };
  const t = bsonType(value);
  if (t === 'ObjectId' || t === 'ObjectID') return { $oid: value.toHexString() };
  if (t === 'Binary') return { $binary: '<binary>' };
  if (t) return { [`$${t.charAt(0).toLowerCase()}${t.slice(1)}`]: String(value) };
  if (Buffer.isBuffer(value)) return { $binary: `<${value.length} bytes>` };
  if (Array.isArray(value)) return value.map(toEvidence);
  if (value !== null && typeof value === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = toEvidence(v);
    return out;
  }
  return value;
}

module.exports = {
  HEX24,
  EjsonError,
  fromExtendedJson,
  coerceIdFields,
  prepareQuery,
  idLikeStringFields,
  toEvidence,
};
