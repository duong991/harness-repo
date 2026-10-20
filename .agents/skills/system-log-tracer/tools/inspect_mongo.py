#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymongo==4.10.1"]
# ///
"""
inspect_mongo.py - Strict read-only MongoDB inspection utility.

Run with `uv run --script tools/inspect_mongo.py ...` so the pinned
`pymongo` dependency resolves automatically; this file never bundles or
requires a workspace-local copy of the driver.

Every operation is checked by mongo_guard.py before it reaches the driver:
only find / countDocuments / distinct / aggregate ever run, and aggregate
pipelines containing $out or $merge (at any nesting depth) are rejected.
Filters and pipelines accept MongoDB Extended JSON ({"$oid"}/{"$date"})
anywhere, and only `_id` fields (including inside $eq/$ne/$in/$nin) coerce a
bare 24-hex string automatically; other fields are never guessed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from common import add_common_args, cfg, redact_sensitive
from mongo_guard import (
    bounded_pipeline,
    bounded_values,
    EjsonError,
    id_like_string_fields,
    prepare_query,
    to_evidence,
    validate_mongo_operation,
)


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Strict read-only MongoDB inspection utility")
    add_common_args(parser)
    parser.add_argument("--db", help="Target database (default: first db in the selected environment's mongo.dbs)")
    parser.add_argument("--collection", help="Target collection to inspect")
    parser.add_argument(
        "--filter", default="{}",
        help='JSON filter, e.g. \'{"userId": {"$oid": "<24 hex>"}}\'. A 24-hex string '
             "under _id is converted automatically; other fields never are.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum documents to return (default: 5, max: 50)")
    parser.add_argument("--count", action="store_true", help="Count matching documents (countDocuments)")
    parser.add_argument("--distinct", help="Return distinct values of a field (distinct)")
    parser.add_argument(
        "--pipeline",
        help="Read-only aggregation pipeline (aggregate) JSON array; same $oid/$date rules; "
             "rejects $out/$merge at any depth",
    )
    parser.add_argument("--list-collections", action="store_true", help="List all collections in target database")
    parser.add_argument("--list-dbs", action="store_true", help="List all databases on the MongoDB cluster")
    return parser


def parse_json_arg(name, value):
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        print(f"ERROR parsing --{name} JSON: {exc}", file=sys.stderr)
        raise SystemExit(1)


def sanitize_uri(uri):
    return re.sub(r"//[^:]+:[^@]+@", "//***:***@", uri or "")


def empty_result_hint(value):
    fields = id_like_string_fields(value)
    if not fields:
        return None
    return (
        f"0 matches. Field(s) {', '.join(fields)} were queried as plain strings; if they "
        'are stored as ObjectId, re-run with {"<field>": {"$oid": "<hex>"}}. A '
        "string-vs-ObjectId difference is evidence to report, not something to fix in "
        "this skill or in application code."
    )


def main(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    limit = max(1, min(50, args.limit))

    # Argument and JSON parsing happen before the pymongo import below so a
    # malformed --filter/--pipeline is reported without ever needing the
    # driver to be installed.
    parsed_filter = parse_json_arg("filter", args.filter)
    parsed_pipeline = parse_json_arg("pipeline", args.pipeline) if args.pipeline is not None else None

    c = cfg(env=args.env, root=args.root, confirm_prod=args.confirm_prod)

    try:
        from bson import ObjectId
        from pymongo import MongoClient
    except ImportError:
        print(
            "ERROR: pymongo is not installed in this Python environment. Run it as "
            "`uv run --script tools/inspect_mongo.py ...` so the pinned dependency "
            "(pymongo==4.10.1) resolves automatically.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    def prepare(parsed, name):
        try:
            return prepare_query(parsed, ObjectId)
        except EjsonError as exc:
            print(f"ERROR in --{name}: {exc}", file=sys.stderr)
            raise SystemExit(1)

    db_name = args.db or (c["mongo_dbs"][0] if c["mongo_dbs"] else None)

    uri = c["mongo_uri"]
    if c["mongo_user"] and c["mongo_pass"] and "@" not in uri:
        from urllib.parse import quote
        user_enc = quote(c["mongo_user"], safe="")
        pass_enc = quote(c["mongo_pass"], safe="")
        uri = re.sub(r"^(mongodb(?:\+srv)?://)", rf"\1{user_enc}:{pass_enc}@", uri)

    client = MongoClient(uri, tz_aware=True, serverSelectionTimeoutMS=5000)
    try:
        if args.list_dbs:
            info = client.admin.command("listDatabases")
            print(json.dumps({
                "cluster": sanitize_uri(uri),
                "databases": [
                    {"name": d.get("name"), "sizeOnDisk": d.get("sizeOnDisk"), "empty": d.get("empty")}
                    for d in info.get("databases", [])
                ],
            }, indent=2, default=str))
            return

        if not db_name:
            print("ERROR: --db is required (no mongo.dbs configured for this environment)", file=sys.stderr)
            raise SystemExit(1)

        db = client[db_name]

        if args.list_collections:
            print(json.dumps({"database": db_name, "collections": db.list_collection_names()}, indent=2))
            return

        if not args.collection:
            print("ERROR: --collection <name> is required (or use --list-collections, --list-dbs)", file=sys.stderr)
            raise SystemExit(1)
        collection = db[args.collection]

        if parsed_pipeline is not None:
            pipeline = prepare(parsed_pipeline, "pipeline")
            validate_mongo_operation("aggregate", {"pipeline": pipeline})
            docs = list(collection.aggregate(bounded_pipeline(pipeline, limit), allowDiskUse=False))
            out = {
                "database": db_name,
                "collection": args.collection,
                "pipeline": to_evidence(pipeline, ObjectId),
                "returned": len(docs),
                "documents": redact_sensitive(to_evidence(docs, ObjectId), c["redaction_fields"]),
            }
            if not docs:
                hint = empty_result_hint(pipeline)
                if hint:
                    out["hint"] = hint
            print(json.dumps(out, indent=2, default=str))
            return

        if args.distinct:
            validate_mongo_operation("distinct")
            filt = prepare(parsed_filter, "filter")
            values, total = bounded_values(collection.distinct(args.distinct, filt))
            print(json.dumps({
                "database": db_name,
                "collection": args.collection,
                "field": args.distinct,
                "filter": to_evidence(filt, ObjectId),
                "distinctTotal": total,
                "valuesReturned": len(values),
                "values": redact_sensitive(to_evidence(values, ObjectId), c["redaction_fields"]),
            }, indent=2, default=str))
            return

        filt = prepare(parsed_filter, "filter")

        if args.count:
            validate_mongo_operation("countDocuments")
            count = collection.count_documents(filt)
            out = {
                "database": db_name,
                "collection": args.collection,
                "filter": to_evidence(filt, ObjectId),
                "count": count,
            }
            if not count:
                hint = empty_result_hint(filt)
                if hint:
                    out["hint"] = hint
            print(json.dumps(out, indent=2, default=str))
        else:
            validate_mongo_operation("find")
            docs = list(collection.find(filt).limit(limit))
            out = {
                "database": db_name,
                "collection": args.collection,
                "filter": to_evidence(filt, ObjectId),
                "returned": len(docs),
                "documents": redact_sensitive(to_evidence(docs, ObjectId), c["redaction_fields"]),
            }
            if not docs:
                hint = empty_result_hint(filt)
                if hint:
                    out["hint"] = hint
            print(json.dumps(out, indent=2, default=str))
    except SystemExit:
        raise
    except Exception as exc:
        print(f"ERROR querying MongoDB ({sanitize_uri(uri)}/{db_name}): {exc}", file=sys.stderr)
        raise SystemExit(2)
    finally:
        client.close()


if __name__ == "__main__":
    main()
