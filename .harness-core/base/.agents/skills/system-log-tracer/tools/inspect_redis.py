#!/usr/bin/env python3
"""
inspect_redis.py - Strict read-only Redis inspection utility for sessions,
caches, and rate limits. Pure stdlib socket-based RESP client.
"""
import argparse
import json
import socket
import sys

from common import add_common_args, cfg, redact_sensitive, dump

ALLOWED_READ_COMMANDS = {
    "PING", "GET", "MGET", "HGET", "HGETALL", "HKEYS", "HLEN",
    "TTL", "PTTL", "TYPE", "EXISTS", "SCAN", "SMEMBERS",
    "SCARD", "ZRANGE", "ZCARD", "INFO", "DBSIZE",
}


class ReadOnlyRedisClient:
    def __init__(self, host="127.0.0.1", port=6379, password=None, timeout=5.0):
        self.host = host
        self.port = int(port)
        self.password = password
        self.timeout = timeout

    def execute(self, cmd, *args):
        cmd_upper = cmd.upper()
        if cmd_upper not in ALLOWED_READ_COMMANDS:
            raise PermissionError(
                f"Command '{cmd}' is BLOCKED. This tool is strictly read-only.\n"
                f"Permitted commands: {sorted(ALLOWED_READ_COMMANDS)}"
            )

        sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        try:
            if self.password:
                self._send(sock, "AUTH", self.password)
                r = self._read(sock)
                if isinstance(r, Exception):
                    raise RuntimeError(f"Redis AUTH failed: {r}")

            self._send(sock, cmd_upper, *args)
            return self._read(sock)
        finally:
            sock.close()

    def _send(self, sock, *args):
        parts = [f"*{len(args)}\r\n".encode("utf-8")]
        for a in args:
            encoded = str(a).encode("utf-8")
            parts.append(f"${len(encoded)}\r\n".encode("utf-8"))
            parts.append(encoded + b"\r\n")
        sock.sendall(b"".join(parts))

    def _read(self, sock):
        f = sock.makefile("rb")
        return self._parse(f)

    def _parse(self, f):
        line = f.readline()
        if not line:
            return None
        prefix, payload = line[:1], line[1:-2]
        if prefix == b"+":
            return payload.decode("utf-8", errors="replace")
        elif prefix == b"-":
            return RuntimeError(payload.decode("utf-8", errors="replace"))
        elif prefix == b":":
            return int(payload)
        elif prefix == b"$":
            length = int(payload)
            if length == -1:
                return None
            data = f.read(length)
            f.read(2)
            return data.decode("utf-8", errors="replace")
        elif prefix == b"*":
            count = int(payload)
            if count == -1:
                return None
            return [self._parse(f) for _ in range(count)]
        return payload.decode("utf-8", errors="replace")


def parse_redis_value(val, redaction_fields=None):
    if val is None:
        return None
    if isinstance(val, list):
        return [parse_redis_value(x, redaction_fields) for x in val]
    try:
        parsed = json.loads(val)
        return redact_sensitive(parsed, redaction_fields)
    except Exception:
        return redact_sensitive(val, redaction_fields)


def main():
    p = argparse.ArgumentParser(description="Strict read-only Redis inspection utility")
    add_common_args(p)
    p.add_argument("--host", help="Redis host override (default: environment config)")
    p.add_argument("--port", type=int, help="Redis port override (default: environment config)")
    p.add_argument("--cmd", default="GET", help="Read-only command: GET, HGETALL, TTL, TYPE, SCAN, INFO, etc. (KEYS is blocked; use SCAN)")
    p.add_argument("--key", help="Target Redis key")
    p.add_argument("--field", help="Hash field name (for HGET)")
    p.add_argument("--pattern", default="*", help="Pattern for SCAN (default: *)")
    p.add_argument("--count", type=int, default=50, help="Count for SCAN")
    args = p.parse_args()

    c = cfg()
    host = args.host or c["redis_host"]
    port = args.port or c["redis_port"]
    password = c["redis_pass"]
    rf = c["redaction_fields"]

    client = ReadOnlyRedisClient(host=host, port=port, password=password, timeout=c["timeout"])

    cmd = args.cmd.upper()
    try:
        if cmd == "GET":
            if not args.key:
                print("ERROR: --key is required for GET command", file=sys.stderr)
                sys.exit(1)
            val = client.execute("GET", args.key)
            ttl = client.execute("TTL", args.key)
            typ = client.execute("TYPE", args.key)
            dump({"key": args.key, "type": typ, "ttl_seconds": ttl, "value": parse_redis_value(val, rf)}, rf)

        elif cmd == "HGETALL":
            if not args.key:
                print("ERROR: --key is required for HGETALL command", file=sys.stderr)
                sys.exit(1)
            raw = client.execute("HGETALL", args.key)
            hash_dict = {}
            if isinstance(raw, list):
                for i in range(0, len(raw), 2):
                    if i + 1 < len(raw):
                        hash_dict[raw[i]] = parse_redis_value(raw[i + 1], rf)
            ttl = client.execute("TTL", args.key)
            dump({"key": args.key, "type": "hash", "ttl_seconds": ttl, "fields": hash_dict}, rf)

        elif cmd == "SCAN":
            scan_res = client.execute("SCAN", 0, "MATCH", args.pattern, "COUNT", args.count)
            keys = scan_res[1] if isinstance(scan_res, list) and len(scan_res) > 1 else []
            dump({"pattern": args.pattern, "count": len(keys) if keys else 0, "keys": (keys or [])[:100]}, rf)

        elif cmd == "TTL":
            if not args.key:
                print("ERROR: --key is required for TTL command", file=sys.stderr)
                sys.exit(1)
            ttl = client.execute("TTL", args.key)
            dump({"key": args.key, "ttl_seconds": ttl}, rf)

        elif cmd == "TYPE":
            if not args.key:
                print("ERROR: --key is required for TYPE command", file=sys.stderr)
                sys.exit(1)
            typ = client.execute("TYPE", args.key)
            dump({"key": args.key, "type": typ}, rf)

        elif cmd == "PING":
            res = client.execute("PING")
            dump({"ping": res}, rf)

        elif cmd == "INFO":
            info_str = client.execute("INFO")
            sections = {}
            curr = "general"
            for line in str(info_str).splitlines():
                if line.startswith("#"):
                    curr = line.strip("# ").strip()
                    sections[curr] = {}
                elif ":" in line:
                    k, v = line.split(":", 1)
                    if curr not in sections:
                        sections[curr] = {}
                    sections[curr][k.strip()] = v.strip()
            dump(sections, rf)

        else:
            args_list = [args.key] if args.key else []
            if args.field:
                args_list.append(args.field)
            res = client.execute(cmd, *args_list)
            dump({"command": cmd, "result": parse_redis_value(res, rf)}, rf)

    except PermissionError as pe:
        print(f"SECURITY ERROR: {pe}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR connecting to Redis ({host}:{port}): {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
