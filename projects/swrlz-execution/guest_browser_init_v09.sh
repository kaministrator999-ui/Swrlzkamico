#!/bin/sh
# Fixed guest-only init. No incoming project code or host paths.
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
exec </dev/null >/dev/console 2>&1
set -eu
finish(){ /bin/busybox poweroff -f || /sbin/poweroff -f; }
trap finish EXIT
mountpoint -q /proc || mount -t proc proc /proc
mountpoint -q /sys || mount -t sysfs sysfs /sys
mountpoint -q /dev || mount -t devtmpfs devtmpfs /dev
mkdir -p /dev/shm /tmp /run
mountpoint -q /dev/shm || mount -t tmpfs -o size=256m tmpfs /dev/shm
chmod 1777 /tmp /dev/shm
nonce="$(sed -n 's/.*swrlz_nonce=\([a-f0-9]*\).*/\1/p' /proc/cmdline)"
[ "${#nonce}" = 32 ] || exit 1
[ "$(ls /sys/class/net)" = lo ] || exit 1
[ ! -e /dev/kvm ] || exit 1
[ -b /dev/vda ] || exit 1
[ ! -e /dev/sda ] && [ ! -e /dev/vdb ] || exit 1
echo "SWRLZ_V09_GUEST_READY:$nonce"
mkdir -p /tmp/renderer
chown renderer:renderer /tmp/renderer
chmod 700 /tmp/renderer
# Native sandbox is required; there is intentionally no --no-sandbox fallback.
browser(){
  timeout -k 5 110 runuser -u renderer -- env -i PATH=/usr/bin:/bin HOME=/home/renderer XDG_RUNTIME_DIR=/tmp/renderer \
    chromium --headless --disable-dev-shm-usage --disable-background-networking \
    --disable-sync --disable-component-update --no-first-run --use-angle=swiftshader \
    --enable-unsafe-swiftshader --user-data-dir=/tmp/renderer/profile "$@"
}
browser --dump-dom file:///opt/swrlz-fixture.html >/tmp/dom.out 2>/tmp/chromium.err || { echo SWRLZ_V09_BROWSER_FAILED; exit 1; }
grep -F '<p id="result">SWRLZ_BROWSER_PASS</p>' /tmp/dom.out >/dev/null || { echo SWRLZ_V09_DOM_FAILED; exit 1; }
echo "SWRLZ_V09_DOM_PASS:$nonce"
browser --screenshot=/tmp/renderer/shot.png --window-size=640,480 file:///opt/swrlz-fixture.html >/tmp/shot.out 2>/tmp/shot.err || { echo SWRLZ_V09_SCREENSHOT_FAILED; exit 1; }
[ "$(od -An -tx1 -N8 /tmp/renderer/shot.png | tr -d ' \n')" = 89504e470d0a1a0a ] || exit 1
[ "$(wc -c </tmp/renderer/shot.png)" -gt 100 ] || exit 1
hash="$(sha256sum /tmp/renderer/shot.png | cut -d' ' -f1)"
echo "SWRLZ_V09_SCREENSHOT:$nonce:$hash"
echo "SWRLZ_V09_COMPLETE:$nonce"
