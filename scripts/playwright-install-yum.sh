#!/bin/bash
# Install Playwright Chromium on yum-based systems (CentOS, RHEL, Amazon Linux).
# Run from repo root: ./scripts/playwright-install-yum.sh
# Or: bash scripts/playwright-install-yum.sh

set -e

echo "Installing Chromium dependencies via yum..."
sudo yum install -y \
  atk \
  at-spi2-atk \
  cups-libs \
  libdrm \
  libxcb \
  libxkbcommon \
  at-spi2-core \
  libX11 \
  libXcomposite \
  libXdamage \
  libXext \
  libXfixes \
  libXrandr \
  mesa-libgbm \
  pango \
  cairo \
  alsa-lib

echo "Installing Playwright Chromium browser binary (no apt)..."
python3 -m playwright install chromium

echo "Done. Use Playwright in Python with: pip install playwright && python3 -m playwright install chromium"
