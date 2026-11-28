#!/bin/bash
# Upgrade only the existing fixed browser QA program and add desktop profiles.
set -Eeuo pipefail
test "$(id -u)" = 0
test $# = 1
GATE=/usr/local/bin/swrlz-deploy-gate
QA=/usr/local/libexec/swrlz-engine-browser-qa.py
PY=/srv/swrlz/browser-venv/bin/python
for f in "$GATE" "$QA"; do
  test -f "$f" && test ! -L "$f" && test "$(stat -c %u "$f")" = 0
done
test -x /usr/bin/chromium && test -x "$PY"
grep -Fq '# SWRLZ_ENGINE_GATE_V1' "$GATE"
grep -Fq 'swrlz-engine-browser-live)' "$GATE"
grep -Fq 'swrlz-engine-browser-candidate)' "$GATE"
sudo -u swrlz-deploy "$PY" -I -c 'import playwright.sync_api'
install -m 0644 -o root -g root "$1" "$QA.new"
/usr/bin/python3 -I -c 'import ast,sys;ast.parse(open(sys.argv[1]).read())' "$QA.new"
# Preserve the working mobile-only version, and generate fixed command entries.
if ! test -e "$QA.pre-desktop"; then cp -p "$QA" "$QA.pre-desktop"; fi
if ! test -e "$GATE.pre-desktop"; then cp -p "$GATE" "$GATE.pre-desktop"; fi
/usr/bin/python3 -I - "$GATE" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);s=p.read_text()
a='case "${SSH_ORIGINAL_COMMAND:-}" in\n'
assert s.count(a)==1
b='''  swrlz-engine-browser-live-desktop) exec /usr/bin/timeout 240 /srv/swrlz/browser-venv/bin/python -I /usr/local/libexec/swrlz-engine-browser-qa.py live desktop ;;
  swrlz-engine-browser-candidate-desktop) exec /usr/bin/timeout 240 /srv/swrlz/browser-venv/bin/python -I /usr/local/libexec/swrlz-engine-browser-qa.py candidate desktop ;;
'''
if 'swrlz-engine-browser-live-desktop)' not in s:
    assert 'swrlz-engine-browser-candidate-desktop)' not in s
    s=s.replace(a,a+b)
else:
    assert b in s
p.with_name(p.name+'.new').write_text(s)
PY
chmod 0755 "$GATE.new"
sh -n "$GATE.new"
mv "$QA.new" "$QA"
mv "$GATE.new" "$GATE"
sudo -u swrlz-deploy env SSH_ORIGINAL_COMMAND=swrlz-engine-check "$GATE"
echo SWRLZ_ENGINE_DESKTOP_BROWSER_READY
