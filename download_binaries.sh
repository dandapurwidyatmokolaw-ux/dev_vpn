#!/usr/bin/env bash
# Script untuk mengunduh binary Mihomo (Clash.Meta) untuk Linux / WSL
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BIN="$SCRIPT_DIR/mihomo"

if [ -f "$TARGET_BIN" ]; then
    echo "[Info] Binary mihomo sudah ada di $TARGET_BIN"
    exit 0
fi

echo "=== Mengunduh binary Mihomo (Clash.Meta) ==="
ARCH="$(uname -m)"
case "$ARCH" in
    x86_64) MIHOMO_ARCH="linux-amd64" ;;
    aarch64) MIHOMO_ARCH="linux-arm64" ;;
    *) echo "Arsitektur $ARCH belum didukung otomatis."; exit 1 ;;
esac

LATEST_TAG=$(curl -s https://api.github.com/repos/MetaCubeX/mihomo/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "$LATEST_TAG" ]; then
    LATEST_TAG="v1.19.32"
fi

DOWNLOAD_URL="https://github.com/MetaCubeX/mihomo/releases/download/${LATEST_TAG}/mihomo-${MIHOMO_ARCH}-${LATEST_TAG}.gz"
echo "Mengunduh dari $DOWNLOAD_URL ..."

curl -L -o /tmp/mihomo.gz "$DOWNLOAD_URL"
gzip -d -f /tmp/mihomo.gz
mv /tmp/mihomo "$TARGET_BIN"
chmod +x "$TARGET_BIN"

echo "=== Selesai! Binary siap di: $TARGET_BIN ==="
