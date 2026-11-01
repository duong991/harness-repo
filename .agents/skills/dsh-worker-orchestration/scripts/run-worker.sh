#!/usr/bin/env bash
# Run one dsh headless worker inside a git worktree and print one JSON line:
#   {"outcome": ..., "exit_code": ..., "duration_s": ..., "run_dir": ..., "detail": ...}
# outcome: finished | no_answer | timeout | runtime_unavailable | failed | preflight_failed
# The script never retries, never touches the user's checkout, and stores
# stdout/stderr only in --run-dir.
set -u

usage() {
  echo "usage: run-worker.sh --worktree DIR --prompt-file FILE --run-dir DIR [--timeout SECS] [--allow-main-worktree]" >&2
}

WT="" PROMPT="" RUN="" TIMEOUT=600 ALLOW_MAIN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --worktree) WT="$2"; shift 2 ;;
    --prompt-file) PROMPT="$2"; shift 2 ;;
    --run-dir) RUN="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --allow-main-worktree) ALLOW_MAIN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 64 ;;
  esac
done

json_escape() { python3 -I -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'; }

SESSION_ID=""

emit() { # outcome exit_code duration detail
  local detail
  detail=$(printf '%s' "$4" | json_escape)
  local sid_json
  sid_json=$( [ -n "${SESSION_ID:-}" ] && printf '"%s"' "$SESSION_ID" || printf 'null' )
  printf '{"outcome": "%s", "exit_code": %s, "duration_s": %s, "session_id": %s, "run_dir": %s, "detail": %s}\n' \
    "$1" "$2" "$3" "$sid_json" "$(printf '%s' "$RUN" | json_escape)" "$detail"
  if [ -n "$RUN" ] && [ -d "$RUN" ]; then
    printf '{"outcome": "%s", "exit_code": %s, "duration_s": %s, "session_id": %s, "detail": %s}\n' \
      "$1" "$2" "$3" "$sid_json" "$detail" > "$RUN/result.json"
  fi
}

fail_pre() { emit preflight_failed null 0 "$1"; exit 2; }
unavailable() { emit runtime_unavailable null 0 "$1"; exit 3; }

# --- preflight: arguments and worktree -------------------------------------
[ -n "$WT" ] && [ -n "$PROMPT" ] && [ -n "$RUN" ] || { usage; fail_pre "missing required argument"; }
case "$TIMEOUT" in ''|*[!0-9]*) fail_pre "--timeout must be whole seconds" ;; esac
[ -d "$WT" ] || fail_pre "worktree not found: $WT"
[ -r "$PROMPT" ] || fail_pre "prompt file not readable: $PROMPT"
TASK=$(cat "$PROMPT")
[ -n "${TASK//[[:space:]]/}" ] || fail_pre "prompt file is empty"

top=$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null) || fail_pre "not a git worktree: $WT"
gitdir=$(cd "$WT" && cd "$(git rev-parse --git-dir)" && pwd -P)
common=$(cd "$WT" && cd "$(git rev-parse --git-common-dir)" && pwd -P)
main_repo=$(cd "$common/.." && pwd -P)
if [ "$gitdir" = "$common" ] && [ "$ALLOW_MAIN" -ne 1 ]; then
  fail_pre "$WT is a main checkout, not a linked worktree; create one with 'git worktree add'"
fi

mkdir -p "$RUN" || fail_pre "cannot create run dir: $RUN"
case "$(cd "$RUN" && pwd -P)/" in
  "$(cd "$top" && pwd -P)/"*) fail_pre "run dir must be outside the worktree (logs would show up in the diff)" ;;
esac

# --- preflight: runtime -----------------------------------------------------
DSH="${DSH_BIN:-$(command -v dsh || true)}"
[ -n "$DSH" ] && [ -x "$DSH" ] || unavailable "dsh not found; install @deepseek-ai/dsh or set DSH_BIN"

NODE_DIR=""
if head -n 1 "$(python3 -I -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$DSH")" | grep -q node; then
  # dsh is a Node script. Under Node < 21 it exits 0 silently, so pin the node
  # that was installed alongside it (nvm layout) and check its version.
  NODE="${DSH_NODE:-$(dirname "$DSH")/node}"
  [ -x "$NODE" ] || NODE=$(command -v node || true)
  [ -n "$NODE" ] || unavailable "node not found for dsh"
  major=$("$NODE" -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
  [ "$major" -ge 21 ] 2>/dev/null || unavailable "dsh needs Node >= 21, found $("$NODE" --version 2>/dev/null) at $NODE; set DSH_NODE"
  NODE_DIR=$(dirname "$NODE")
fi

TIMEOUT_CMD=$(command -v timeout || command -v gtimeout || true)

# --- auto-sync model/provider configuration from desktop profile -------
DESKTOP_PATCH="$HOME/.dsh/profiles/desktop/cordis.patch.yml"
HEADLESS_PATCH="$HOME/.dsh/profiles/headless/cordis.patch.yml"
if [ -r "$DESKTOP_PATCH" ]; then
  python3 -c "
import os, yaml
dp = os.path.expanduser('$DESKTOP_PATCH')
hp = os.path.expanduser('$HEADLESS_PATCH')
if os.path.exists(dp):
    with open(dp) as f:
        d = yaml.safe_load(f) or []
    models = {'llm-pi-ai', 'agent-default-model', 'llm-deepseek', 'web-search-deepseek'}
    relevant = [p for p in d if p.get('id') in models]
    with open(hp, 'w') as f:
        yaml.dump(relevant, f, allow_unicode=True, sort_keys=False)
" 2>/dev/null || true
fi

# --- auto-resolve credentials from ~/.dsh/.credentials.yaml if unset --------
CREDS_FILE="$HOME/.dsh/.credentials.yaml"
if [ -r "$CREDS_FILE" ]; then
  if [ -z "${G9ROUTER_API_KEY:-}" ]; then
    G9_VAL=$(python3 -c 'import yaml, os, sys; c=yaml.safe_load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}; print(c.get("refs", {}).get("G9ROUTER_API_KEY", ""))' "$CREDS_FILE" 2>/dev/null || true)
    [ -z "$G9_VAL" ] && G9_VAL=$(awk -F': ' '/G9ROUTER_API_KEY:/ {print $2}' "$CREDS_FILE" | tr -d ' "' | head -n 1)
    [ -n "$G9_VAL" ] && export G9ROUTER_API_KEY="$G9_VAL"
  fi
  if [ -z "${ANYROUTE_API_KEY:-}" ]; then
    ANY_VAL=$(python3 -c 'import yaml, os, sys; c=yaml.safe_load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}; print(c.get("refs", {}).get("ANYROUTE_API_KEY", ""))' "$CREDS_FILE" 2>/dev/null || true)
    [ -z "$ANY_VAL" ] && ANY_VAL=$(awk -F': ' '/ANYROUTE_API_KEY:/ {print $2}' "$CREDS_FILE" | tr -d ' "' | head -n 1)
    [ -n "$ANY_VAL" ] && export ANYROUTE_API_KEY="$ANY_VAL"
  fi
  if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
    DS_VAL=$(python3 -c 'import yaml, os, sys; c=yaml.safe_load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}; print(c.get("refs", {}).get("DEEPSEEK_API_KEY", ""))' "$CREDS_FILE" 2>/dev/null || true)
    [ -z "$DS_VAL" ] && DS_VAL=$(awk -F': ' '/DEEPSEEK_API_KEY:/ {print $2}' "$CREDS_FILE" | tr -d ' "' | head -n 1)
    [ -n "$DS_VAL" ] && export DEEPSEEK_API_KEY="$DS_VAL"
  fi
fi

# --- run --------------------------------------------------------------------
printf '%s\n' "$TASK" > "$RUN/prompt.txt"
git -C "$WT" rev-parse HEAD > "$RUN/base.txt" 2>/dev/null
start=$(date +%s)
(
  cd "$WT" || exit 70
  [ -n "$NODE_DIR" ] && PATH="$NODE_DIR:$PATH"
  if [ -n "$TIMEOUT_CMD" ]; then
    "$TIMEOUT_CMD" -k 10 "$TIMEOUT" "$DSH" --profile headless "$TASK"
  else
    perl -e 'alarm shift; exec @ARGV or exit 127' "$TIMEOUT" "$DSH" --profile headless "$TASK"
  fi
) > "$RUN/stdout.txt" 2> "$RUN/stderr.txt" < /dev/null
code=$?
dur=$(( $(date +%s) - start ))

# --- detect session ID and auto-register to workspace.json ------------------
if [ -d "$WT" ]; then
  SESSION_ID=$(python3 -c "
import os, glob, json, sys
wt = sys.argv[1]
for p in [os.path.realpath(wt), wt]:
    esc = '--' + p.strip('/').replace('/', '-') + '--'
    sdir = os.path.expanduser(f'~/.dsh/sessions/{esc}')
    if os.path.exists(sdir):
        sids = [d for d in glob.glob(f'{sdir}/session-*') if os.path.isdir(d)]
        if sids:
            sids.sort(key=os.path.getmtime, reverse=True)
            sid = os.path.basename(sids[0])
            print(sid)
            main_repo = sys.argv[2] if len(sys.argv) > 2 else ''
            ws_file = os.path.expanduser('~/.dsh/storages/workspace.json')
            if main_repo and os.path.exists(ws_file):
                with open(ws_file) as f:
                    ws_data = json.load(f)
                rmain = os.path.realpath(main_repo)
                for wid, ws in ws_data.get('tables', {}).get('workspaces', {}).items():
                    if os.path.realpath(ws.get('path', '')) == rmain:
                        if sid not in ws.setdefault('sessionIds', []):
                            ws['sessionIds'].append(sid)
                            with open(ws_file, 'w') as f:
                                json.dump(ws_data, f, indent=2, ensure_ascii=False)
            break
" "$WT" "$main_repo" 2>/dev/null || true)
  [ -n "$SESSION_ID" ] && printf '%s\n' "$SESSION_ID" > "$RUN/session_id.txt"
fi

last_err=$(grep -E '^dsh: [A-Z_]+:' "$RUN/stderr.txt" | tail -n 1)
if [ "$code" -eq 124 ] || [ "$code" -eq 137 ] || [ "$code" -eq 142 ]; then
  emit timeout "$code" "$dur" "killed after ${TIMEOUT}s; worktree state unknown"
elif [ "$code" -ne 0 ]; then
  case "$last_err" in
    *MISSING_CREDENTIAL*|*model-unavailable*|*MODEL_UNAVAILABLE*) emit runtime_unavailable "$code" "$dur" "$last_err" ;;
    *) emit failed "$code" "$dur" "${last_err:-$(tail -n 3 "$RUN/stderr.txt")}" ;;
  esac
elif [ -z "$(tr -d '[:space:]' < "$RUN/stdout.txt")" ]; then
  emit no_answer 0 "$dur" "exit 0 but no final answer on stdout"
else
  emit finished 0 "$dur" "$(head -c 300 "$RUN/stdout.txt")"
fi
