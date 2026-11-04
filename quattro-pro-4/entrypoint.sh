#!/usr/bin/env bash
# entrypoint.sh 'DOS command' ...   Each argument is one DOS command, run from C:\QPRO
# with the host folder mounted at /work as C:\WORK.
# Environment:
#   KEYS       keystrokes to feed in (mk.py syntax), e.g. '{w5}/fr{enter}'
#   SHOT_AT    space-separated seconds after start at which to save /work/shot-<s>.png
#   TIMEOUT    kill DOSBox-X after this many seconds (default 120)
set -euo pipefail
C=/opt/qp/c
rm -rf "$C/WORK" && ln -s /work "$C/WORK"   # DOSBox-X follows the symlink
[ -n "${KEYS:-}" ] && python3 /opt/qp/mk.py "$C/KEYS.DAT" "$KEYS"
{
  cat <<CONF
[sdl]
autolock=false
[dosbox]
memsize=16
machine=svga_s3
quit warning=false
[cpu]
cycles=max
[dos]
files=60
[autoexec]
mount c "$C" -nocachedir
c:
set PATH=C:\\QPRO;%PATH%
CONF
  [ -n "${KEYS:-}" ] && echo 'KEYS.COM'
  echo 'cd \WORK'
  printf '%s\n' "$@"
  echo 'exit'
} > /tmp/dosbox.conf

export DISPLAY=:99
Xvfb :99 -screen 0 800x600x24 >/dev/null 2>&1 &
sleep 1
dosbox-x -conf /tmp/dosbox.conf -nopromptfolder -fastlaunch >/tmp/dbx.log 2>&1 &
PID=$!
for s in ${SHOT_AT:-}; do
  ( sleep "$s"; import -display :99 -window root "/work/shot-$s.png" ) &
done
( sleep "${TIMEOUT:-120}"; kill $PID 2>/dev/null ) &
wait $PID || true
