#!/usr/bin/env bash
# Provision a native NS-2.35+nOBS tree without manual Makefile edits.
# Usage: bash provision_native_ns.sh [--clean]
set -Eeuo pipefail
IFS=$'\n\t'

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${NOBS_BUILD_ROOT:-$BASE/build}"
ARCHIVE="${NS235_ARCHIVE:-$ROOT/sources/ns-allinone-2.35.tar.gz}"
URL="${NS235_URL:-https://downloads.sourceforge.net/project/nsnam/allinone/ns-allinone-2.35.tar.gz}"
EXPECTED_SHA256="2216f4e8e274f5c2437741fc6e9c9728369fabe1838c708ef974d262b941cd5d"
TREE="$ROOT/ns-allinone-2.35"
NS_TREE="$TREE/ns-2.35"
NS_BIN="$NS_TREE/ns"
DEPS="$ROOT/deps/libxt"

die() { echo "NATIVE_PROVISION_FAILED: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null || die "missing command: $1"; }

for cmd in tar sha256sum make gcc g++ awk python3; do need "$cmd"; done
mkdir -p "$ROOT/sources"

if [[ "${1:-}" == "--clean" ]]; then
  [[ "${2:-}" == "" ]] || die "usage: bash provision_native_ns.sh [--clean]"
  rm -rf "$TREE"
fi
[[ "${1:-}" == "" || "${1:-}" == "--clean" ]] || die "usage: bash provision_native_ns.sh [--clean]"

if [[ ! -f "$ARCHIVE" ]]; then
  need curl
  echo "Downloading NS-2.35 archive..."
  curl -L --fail --retry 3 --output "$ARCHIVE.part" "$URL"
  mv "$ARCHIVE.part" "$ARCHIVE"
fi
actual="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_SHA256" ]] || die "NS-2.35 SHA-256 mismatch: $actual (expected $EXPECTED_SHA256)"

if [[ ! -d "$TREE" ]]; then
  echo "Extracting NS-2.35..."
  tar -xzf "$ARCHIVE" -C "$ROOT"
fi
[[ -d "$TREE/ns-2.35" ]] || die "invalid archive layout: $TREE/ns-2.35 missing"

# Ubuntu installations may not have libxt-dev although X11 itself is present.
# Extract it locally when apt download is available; no root access is needed.
if [[ ! -f /usr/include/X11/Intrinsic.h && ! -f "$DEPS/usr/include/X11/Intrinsic.h" ]]; then
  need apt-get
  need dpkg-deb
  mkdir -p "$DEPS/download"
  (cd "$DEPS/download" && apt-get download libxt-dev >/dev/null) \
    || die "X11/Intrinsic.h missing; install libxt-dev or make apt-get download available"
  deb="$(find "$DEPS/download" -maxdepth 1 -name 'libxt-dev_*.deb' -print -quit)"
  [[ -n "$deb" ]] || die "libxt-dev package was not downloaded"
  dpkg-deb -x "$deb" "$DEPS"
fi

if [[ -f "$DEPS/usr/include/X11/Intrinsic.h" ]]; then
  export CPPFLAGS="-I$DEPS/usr/include ${CPPFLAGS:-}"
  export LDFLAGS="-L$DEPS/usr/lib/x86_64-linux-gnu ${LDFLAGS:-}"
  export LD_LIBRARY_PATH="$DEPS/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

echo "Preparing NS-2.35 base dependencies..."
if [[ ! -x "$TREE/bin/tclsh8.5" ]]; then
  echo "Building NS-2.35 base dependencies..."
  (cd "$TREE" && ./install)
fi

[[ -f "$NS_TREE/Makefile" ]] || die "NS-2.35 install did not generate: $NS_TREE/Makefile"

echo "Applying versioned nOBS overlay..."
for dir in common mdart optical queue routing tcl tcp; do
  [[ -d "$BASE/nobs/$dir" ]] || die "missing overlay directory: nobs/$dir"
  cp -a "$BASE/nobs/$dir/." "$NS_TREE/$dir/"
done

makefile="$NS_TREE/Makefile"
python3 - "$makefile" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
objects = [
    "optical/op-delay.o", "optical/op-queue.o", "optical/op-burst_agent.o",
    "optical/op-classifier.o", "optical/op-classifier-hash.o",
    "optical/op-classifier-sr.o", "optical/op-sragent.o", "optical/op-queue2.o",
    "optical/op-schedule.o", "optical/op-converterschedule.o",
    "optical/op-fdlschedule.o", "optical/op-bhp-flood-agent.o",
    "optical/op-bhp-guard.o", "optical/op-bhp-audit.o",
]
missing = [obj for obj in objects if obj not in text]
if missing:
    anchor = "\tmdart/mdart.o \\\n"
    if anchor not in text:
        raise SystemExit("Makefile anchor mdart/mdart.o not found")
    block = "\t" + " \\\n\t".join(missing) + " \\\n"
    text = text.replace(anchor, anchor + block, 1)
    path.write_text(text)
print("NOBS_MAKEFILE_OK objects=" + str(len(objects)))
PY

echo "Building NS-2.35+nOBS..."
# NS-2.35's legacy Makefile uses CFLAGS for both C and C++ compilation;
# CXXFLAGS is ignored by its pattern rule. Build the old C++ code with the
# language standard it was written for and keep permissive conversion rules.
export CFLAGS="${CFLAGS:-} -std=gnu++98 -fpermissive"
(cd "$NS_TREE" && make -j"${NS_JOBS:-2}")
[[ -x "$NS_BIN" ]] || die "build completed without executable: $NS_BIN"
echo "NATIVE_PROVISION_OK: $NS_BIN"
