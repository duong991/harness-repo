#!/usr/bin/env node
/**
 * redact.js - Shared redaction for the Node tools. Mirrors
 * tools/common.py's redact_sensitive: masks secrets, emails, phone numbers,
 * and precise coordinate pairs, plus any extra config-provided field names.
 * No dependencies; importable on its own.
 */
'use strict';

const DEFAULT_SENSITIVE_FIELDS = [
  'password', 'pushtoken', 'token', 'refreshtoken', 'accesstoken', 'secret',
  'salt', 'authorization', 'sessionid', 'session_id', 'apikey', 'api_key',
  'email', 'phone', 'phonenumber', 'mobile', 'latitude', 'longitude', 'lat',
  'lng', 'lon', 'coordinates', 'coords',
];

const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
// Bounded by characters that cannot continue an identifier (alphanumerics or
// '-') so hex IDs such as ObjectIds and UUID segments are not mistaken for
// phone numbers.
const PHONE_RE = /(?<![0-9A-Za-z-])\+?\d[\d\-.\s]{7,14}\d(?![0-9A-Za-z-])/g;
const COORD_PAIR_RE = /-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}/g;
const JSON_SECRET_VALUE_RE = /("(?:password|pushToken|token|refreshToken|accessToken|secret|salt|authorization|sessionId|apiKey)"\s*:\s*)"[^"]*"/gi;
const KV_SECRET_VALUE_RE = /((?:password|token|secret|pushToken|apikey)=\s*)[^\s&]+/gi;

function sensitiveKeyPattern(extraFields) {
  const names = new Set(DEFAULT_SENSITIVE_FIELDS.concat((extraFields || []).map((f) => f.toLowerCase())));
  const alt = Array.from(names).sort((a, b) => b.length - a.length).map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  return new RegExp(`^(${alt.join('|')})$`, 'i');
}

function redactValue(value, pattern) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const out = {};
    for (const [k, v] of Object.entries(value)) {
      // Type-preserving Extended JSON wrappers ({"$oid"}, {"$date"}) carry
      // identifiers and timestamps, never personal data: keep them intact.
      if ((k === '$oid' || k === '$date') && typeof v === 'string') out[k] = v;
      else out[k] = pattern.test(k) ? '[REDACTED]' : redactValue(v, pattern);
    }
    return out;
  }
  if (Array.isArray(value)) return value.map((v) => redactValue(v, pattern));
  if (typeof value === 'string') {
    let text = value.replace(JSON_SECRET_VALUE_RE, '$1"[REDACTED]"');
    text = text.replace(KV_SECRET_VALUE_RE, '$1[REDACTED]');
    text = text.replace(COORD_PAIR_RE, '[REDACTED_COORDINATES]');
    text = text.replace(EMAIL_RE, '[REDACTED_EMAIL]');
    text = text.replace(PHONE_RE, '[REDACTED_PHONE]');
    return text;
  }
  return value;
}

function redactSensitive(data, extraFields) {
  return redactValue(data, sensitiveKeyPattern(extraFields));
}

module.exports = { redactSensitive, DEFAULT_SENSITIVE_FIELDS };
