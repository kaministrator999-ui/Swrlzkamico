#!/bin/bash
# Run once as the OVH administrator. The existing restricted SSH gate is retained.
set -Eeuo pipefail
trap 'echo "SWRLZ_ENGINE_INSTALL_FAILED line=$LINENO status=$?" >&2' ERR
test "$(id -u)" = 0
test $# = 1
SOURCE=$1
test -f "$SOURCE"
GATE=/usr/local/bin/swrlz-deploy-gate
LEGACY=/usr/local/bin/swrlz-deploy-gate.pre-engine
PUBLISH=/usr/local/sbin/swrlz-engine-publish
HISTORY=/var/www/.swrlz-engine-releases
HOME_DIR=$(getent passwd swrlz-deploy | cut -d: -f6)
test -n "$HOME_DIR"
test -f "$HOME_DIR/.ssh/authorized_keys"
grep -Fq 'command="/usr/local/bin/swrlz-deploy-gate"' "$HOME_DIR/.ssh/authorized_keys" || { echo 'Unexpected forced command; no gate changes made.' >&2; exit 1; }
test -f "$GATE" && test ! -L "$GATE"
test "$(stat -c '%u' "$GATE")" = 0
test -d /var/www/swrlz-engine && test ! -L /var/www/swrlz-engine
# Never chown the production document tree or alter nginx/authentication.
install -d -m 0700 -o root -g root "$HISTORY"
install -m 0755 -o root -g root "$SOURCE" "$PUBLISH.new"
python3 -m py_compile "$PUBLISH.new"
"$PUBLISH.new" initialize
"$PUBLISH.new" check
if test -f "$PUBLISH" && ! test -e "$PUBLISH.pre-runtime"; then
  install -m 0755 -o root -g root "$PUBLISH" "$PUBLISH.pre-runtime"
fi
mv -f "$PUBLISH.new" "$PUBLISH"
if ! grep -Fq '# SWRLZ_ENGINE_GATE_V1' "$GATE"; then
  test ! -e "$LEGACY"
  install -m 0755 -o root -g root "$GATE" "$LEGACY"
fi
test -x "$LEGACY"
tmp=$(mktemp /etc/sudoers.d/.swrlz-engine.XXXXXX)
trap 'rm -f "$tmp" "$GATE.new"' EXIT
cat >"$tmp" <<'SUDOERS'
swrlz-deploy ALL=(root) NOPASSWD: /usr/local/sbin/swrlz-engine-publish check, /usr/local/sbin/swrlz-engine-publish deploy, /usr/local/sbin/swrlz-engine-publish deploy-runtime, /usr/local/sbin/swrlz-engine-publish rollback
SUDOERS
chmod 0440 "$tmp"
visudo -cf "$tmp"
mv -f "$tmp" /etc/sudoers.d/swrlz-engine
cat >"$GATE.new" <<'GATE'
#!/bin/sh
# SWRLZ_ENGINE_GATE_V1
set -eu
case "${SSH_ORIGINAL_COMMAND:-}" in
  swrlz-engine-check) exec /usr/bin/sudo -n /usr/local/sbin/swrlz-engine-publish check ;;
  swrlz-engine-deploy) exec /usr/bin/sudo -n /usr/local/sbin/swrlz-engine-publish deploy ;;
  swrlz-engine-runtime-deploy) exec /usr/bin/sudo -n /usr/local/sbin/swrlz-engine-publish deploy-runtime ;;
  swrlz-engine-rollback) exec /usr/bin/sudo -n /usr/local/sbin/swrlz-engine-publish rollback ;;
  *) exec /usr/local/bin/swrlz-deploy-gate.pre-engine "$@" ;;
esac
GATE
chmod 0755 "$GATE.new"
sh -n "$GATE.new"
mv -f "$GATE.new" "$GATE"
sudo -u swrlz-deploy env SSH_ORIGINAL_COMMAND=swrlz-engine-check "$GATE"
echo SWRLZ_ENGINE_RUNTIME_BRIDGE_INSTALLED
