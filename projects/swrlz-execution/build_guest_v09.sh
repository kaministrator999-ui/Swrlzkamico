#!/usr/bin/env bash
# Build a clean guest from Debian packages, never copy the host filesystem.
set -euo pipefail
out="$(realpath "$1")"
mkdir -p "$out"
work="$(mktemp -d)"
trap 'sudo rm -rf "$work"' EXIT
root="$work/root"
sudo debootstrap --variant=minbase --include=ca-certificates bookworm "$root" https://deb.debian.org/debian
printf '#!/bin/sh\nexit 101\n' | sudo tee "$root/usr/sbin/policy-rc.d" >/dev/null
sudo chmod 755 "$root/usr/sbin/policy-rc.d"
sudo chroot "$root" apt-get update
sudo chroot "$root" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  linux-image-amd64 initramfs-tools chromium chromium-sandbox libgl1-mesa-dri libegl1 fonts-liberation util-linux busybox-static
sudo chroot "$root" useradd -m -s /bin/sh renderer
sudo install -m 0755 "$(dirname "$0")/guest_browser_init_v09.sh" "$root/usr/local/sbin/swrlz-probe"
sudo install -m 0644 "$(dirname "$0")/guest_browser_fixture_v09.html" "$root/opt/swrlz-fixture.html"
# Ensure virtio root disk support is present in the matching guest initramfs.
printf 'virtio_pci\nvirtio_blk\n' | sudo tee -a "$root/etc/initramfs-tools/modules" >/dev/null
sudo chroot "$root" update-initramfs -u -k all
kernel="$(find "$root/boot" -maxdepth 1 -name 'vmlinuz-*' | sort | tail -1)"
version="$(basename "$kernel" | sed 's/^vmlinuz-//')"
sudo cp "$kernel" "$out/vmlinuz"
sudo cp "$root/boot/initrd.img-$version" "$out/initrd.img"
sudo chroot "$root" apt-get clean
sudo rm -rf "$root/var/lib/apt/lists/"* "$root/var/cache/apt/"*
sudo find "$root/var/log" -type f -delete
sudo truncate -s 0 "$root/etc/machine-id"
sudo rm -f "$root/etc/resolv.conf"
printf 'nameserver 127.0.0.1\n' | sudo tee "$root/etc/resolv.conf" >/dev/null
# Sparse read-only backing image; QEMU uses an ephemeral overlay.
size="$(sudo du -sm "$root" | cut -f1)"
truncate -s "$((size+384))M" "$work/guest.ext4"
sudo mkfs.ext4 -q -F -m 0 -d "$root" "$work/guest.ext4"
gzip -1 -c "$work/guest.ext4" > "$out/guest.ext4.gz"
sudo chown "$(id -u):$(id -g)" "$out/vmlinuz" "$out/initrd.img"
(cd "$out"; sha256sum vmlinuz initrd.img guest.ext4.gz > SHA256SUMS)
