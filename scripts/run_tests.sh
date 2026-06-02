#!/usr/bin/env bash
#
# Run the test suite against a throwaway local Postgres cluster.
# No running database required — this spins one up in a temp dir, runs pytest,
# and tears it all down. Any args are passed through to pytest.
#
#   ./scripts/run_tests.sh                 # run everything
#   ./scripts/run_tests.sh tests/test_pdf.py -v
#
set -euo pipefail
cd "$(dirname "$0")/.."

# --- Locate Postgres binaries (initdb / pg_ctl) ---
PGBIN=""
if command -v initdb >/dev/null 2>&1; then
  PGBIN="$(dirname "$(command -v initdb)")"
else
  for d in /usr/lib/postgresql/*/bin /usr/local/opt/postgresql*/bin /opt/homebrew/opt/postgresql*/bin; do
    [ -x "$d/initdb" ] && PGBIN="$d" && break
  done
fi
[ -n "$PGBIN" ] || { echo "ERROR: Postgres not found (need initdb/pg_ctl). Install postgresql."; exit 1; }

PY="venv/bin/python"; [ -x "$PY" ] || PY="python3"
PORT="${PGPORT:-55432}"
DATADIR="$(mktemp -d)"
SOCKDIR="$(mktemp -d)"

cleanup() {
  "$PGBIN/pg_ctl" -D "$DATADIR" stop -m fast >/dev/null 2>&1 || true
  rm -rf "$DATADIR" "$SOCKDIR"
}
trap cleanup EXIT

echo "→ Initialising throwaway Postgres ($PGBIN) ..."
"$PGBIN/initdb" -D "$DATADIR" -U erp --auth=trust >/dev/null
"$PGBIN/pg_ctl" -D "$DATADIR" -o "-p $PORT -k $SOCKDIR -c listen_addresses=''" -l "$DATADIR/log" start >/dev/null
until "$PGBIN/pg_isready" -h "$SOCKDIR" -p "$PORT" -q; do sleep 0.5; done
"$PGBIN/createdb" -h "$SOCKDIR" -p "$PORT" -U erp erptest

export TEST_DATABASE_URL="postgresql://erp@/erptest?host=$SOCKDIR&port=$PORT"
echo "→ Running pytest ..."
"$PY" -m pytest "$@"
