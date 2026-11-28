#!/bin/bash
# Add only two unprivileged fixed browser actions to the existing SSH gate.
set -Eeuo pipefail
test "$(id -u)" = 0
test $# = 1
GATE=/usr/local/bin/swrlz-deploy-gate
QA=/usr/local/libexec/swrlz-engine-browser-qa.py
PY=/srv/swrlz/browser-venv/bin/python
test -x /usr/bin/chromium && test -x "$PY"
test -f "$GATE" && test ! -L "$GATE"
test "$(stat -c %u "$GATE")" = 0
grep -Fq '# SWRLZ_ENGINE_GATE_V1' "$GATE"
grep -Fq 'swrlz-engine-runtime-deploy)' "$GATE"
sudo -u swrlz-deploy "$PY" -I -c 'import playwright.sync_api'
install -d -m 0755 -o root -g root /usr/local/libexec
install -m 0644 -o root -g root "$1" "$QA.new"
/usr/bin/python3 -I -c 'import ast,sys;ast.parse(open(sys.argv[1]).read())' "$QA.new"
mv "$QA.new" "$QA"
if ! grep -Fq 'swrlz-engine-browser-live)' "$GATE"; then
  test ! -e "$GATE.pre-browser"
  cp -p "$GATE" "$GATE.pre-browser"
  python3 - "$GATE" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);s=p.read_text()
a='case "${SSH_ORIGINAL_COMMAND:-}" in\n'
assert s.count(a)==1
b='''  swrlz-engine-browser-live) exec /usr/bin/timeout 240 /srv/swrlz/browser-venv/bin/python -I /usr/local/libexec/swrlz-engine-browser-qa.py live ;;
  swrlz-engine-browser-candidate) exec /usr/bin/timeout 240 /srv/swrlz/browser-venv/bin/python -I /usr/local/libexec/swrlz-engine-browser-qa.py candidate ;;
'''
p.with_name(p.name+'.new').write_text(s.replace(a,a+b))
PY
  chmod 0755 "$GATE.new"
  sh -n "$GATE.new"
  mv "$GATE.new" "$GATE"
fi
sudo -u swrlz-deploy env SSH_ORIGINAL_COMMAND=swrlz-engine-check "$GATE"
echo SWRLZ_ENGINE_BROWSER_BRIDGE_INSTALLED
