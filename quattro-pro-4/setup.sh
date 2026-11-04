#!/usr/bin/env bash
# Download Borland Quattro Pro 4.0 for DOS from WinWorld, install it, and set up
# a DOSBox-X rig for it.
#
# Usage: setup.sh [target-dir]      (default: ./emu next to this script)
# Needs: curl, 7zz (7-Zip), python3, dosbox-x.
#        macOS: brew install curl sevenzip dosbox-x
#
# Result:
#   <target>/c/QPRO/      installed program (mounted as C:)
#   <target>/dosbox.conf  DOSBox-X config; start it with <target>/run.sh
#
# INSTALL.EXE is interactive, so it is run inside DOSBox-X with KEYS.COM, a tiny
# DOS keystroke feeder (source: keys.asm, input built by mk.py).
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
TARGET=${1:-$HERE/emu}
# "Borland Quattro Pro 4.0 for DOS (2-12-92) (3.5-1.44mb)" on
# https://winworldpc.com/product/quattro-pro/4x ("Server 1").
URL='https://winworldpc.com/download/383e1a33-0d48-11ed-b2b1-0200008a0da4/from/c3ae6ee2-8099-713d-3411-c3a6e280947e'
INSTALL_SECONDS=${INSTALL_SECONDS:-150}

for tool in curl 7zz python3 dosbox-x; do
  command -v "$tool" >/dev/null || { echo "missing: $tool" >&2; exit 1; }
done

mkdir -p "$TARGET"/{download,shots,c/SRC}
cd "$TARGET"

ARCHIVE=download/qp4.7z
if [ ! -s "$ARCHIVE" ]; then
  echo "Downloading Quattro Pro 4.0 ..."
  curl -fL --retry 3 -A 'Mozilla/5.0' -e https://winworldpc.com/ -o "$ARCHIVE.part" "$URL"
  mv "$ARCHIVE.part" "$ARCHIVE"
fi
7zz t "$ARCHIVE" >/dev/null || { echo "bad archive; delete $ARCHIVE and retry" >&2; exit 1; }
echo "archive sha256: $(shasum -a 256 "$ARCHIVE" | cut -d' ' -f1)"

# Both floppies go in C:\SRC, as one folder: INSTALL.EXE asks for disk 2 by
# looking for DISK2.DSK on the source path.
rm -rf download/x && mkdir download/x
7zz x -y -odownload/x "$ARCHIVE" >/dev/null
for img in download/x/*/disk0[12].img; do 7zz x -y -oc/SRC "$img" >/dev/null; done
SERIAL=$(tr -d '[:space:]' < download/x/*/serial.txt)

# KEYS.COM (213 bytes, assembled from keys.asm).
base64 -d > c/KEYS.COM <<'B64'
63MAAAAA1QHVAQAAnC7/HgIBHgZQU1YOH4s2BgE7NggBc0yDPgoBAHQG/w4KAes/uEAAjsAmix4cAInYg8ACJjsGggByBCahgAAmOwYaAHQeUItEAiaJB1gmoxwAg8YEiTYGATs2CAFzBYsEowoBXltYBx/PuAA9uskBzSFyRYnDtD+5AMC61QHNIXI3BdUBowgBtD7NIb7VAYsEowoBuBw1zSGJHgIBjAYEAbgcJboMAc0hixYIAYPCD7EE0+q4ADHNIbgBTM0hQzpcS0VZUy5EQVQA
B64
chmod +x c/KEYS.COM

# INSTALL.EXE screens, in order: welcome, hardware/video (c = continue), source
# and destination (defaults: C:\QPRO), copy, then a registration screen where
# F2 edits each field (name, company, serial), then dismiss the closing screens.
# /B = black-and-white display.
KEYS="{w3}{enter}c{enter}{enter}{enter}{w25}c{w2}{enter}{d0.3}{w1}{f2}user{enter}{enter}{f2}user{enter}{enter}{f2}${SERIAL}{enter}{d3}{enter}{enter}{enter}{enter}{enter}{enter}{enter}{enter}{enter}{enter}{enter}{enter}"
python3 "$HERE/mk.py" c/KEYS.DAT "$KEYS"

conf() {  # conf FILE 'DOS commands, one per line'
  cat > "$1" <<CONF
[sdl]
autolock=false
priority=higher,normal
[dosbox]
memsize=16
machine=svga_s3
quit warning=false
[cpu]
cycles=max
[dos]
files=60
[autoexec]
mount c "$TARGET/c" -nocachedir
c:
$2
CONF
}

if [ ! -s c/QPRO/Q.EXE ]; then
  echo "Running INSTALL.EXE in DOSBox-X (up to ${INSTALL_SECONDS}s) ..."
  conf install.conf 'KEYS.COM
cd \SRC
install /B
exit'
  dosbox-x -conf install.conf -nopromptfolder -fastlaunch >dbx.log 2>&1 &
  PID=$!
  for ((i = 0; i < INSTALL_SECONDS; i++)); do kill -0 $PID 2>/dev/null || break; sleep 1; done
  kill $PID 2>/dev/null || true
  wait $PID 2>/dev/null || true
fi
[ -s c/QPRO/Q.EXE ] && [ -s c/QPRO/Q.VRM ] || {
  echo "install failed: no C:\\QPRO\\Q.EXE (see $TARGET/dbx.log; raise INSTALL_SECONDS)" >&2
  exit 1
}

# Done with the keystroke feeder and the source disks.
rm -f c/KEYS.DAT install.conf
conf dosbox.conf 'set PATH=C:\QPRO;%PATH%
cd \QPRO
Q'
cat > run.sh <<RUN
#!/usr/bin/env bash
exec dosbox-x -conf "$TARGET/dosbox.conf" -nopromptfolder "\$@"
RUN
chmod +x run.sh
echo "Installed to $TARGET/c/QPRO. Start it with: $TARGET/run.sh"
