#!/usr/bin/env bash
# entrypoint.sh 'DOS command' ...   Each argument is one DOS command, run from C:\QPRO
# with the host folder mounted at /work as C:\WORK.
# Environment:
#   KEYS       keystrokes to feed in (mk.py syntax), e.g. '{w5}/fr{enter}'
#   SHOT_AT    space-separated seconds after start at which to save /work/shot-<s>.png
#   GUI        set to 1 to serve the display at http://localhost:6080/vnc.html (publish -p 6080:6080)
#   TIMEOUT    kill DOSBox-X after this many seconds (default 120; 0 = never, the default with GUI)
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
if [ -n "${GUI:-}" ]; then
  # VNC listens on loopback inside the container and needs a random password.
  # Publish the port on loopback only: -p 127.0.0.1:6080:6080
  VNCPASS=$(head -c12 /dev/urandom | base64 | tr -dc 'A-Za-z0-9')
  x11vnc -storepasswd "$VNCPASS" /tmp/vncpass >/dev/null 2>&1
  x11vnc -display :99 -forever -shared -localhost -rfbauth /tmp/vncpass -quiet -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
  websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/ws.log 2>&1 &
  echo "Open http://localhost:6080/vnc.html?autoconnect=1&resize=scale  password: $VNCPASS" >&2
fi
dosbox-x -conf /tmp/dosbox.conf -nopromptfolder -fastlaunch >/tmp/dbx.log 2>&1 &
PID=$!
for s in ${SHOT_AT:-}; do
  ( sleep "$s"; import -display :99 -window root "/work/shot-$s.png" ) &
done
[ -n "${GUI:-}" ] && : "${TIMEOUT:=0}"   # an interactive session has no timeout
if [ "${TIMEOUT:-120}" != 0 ]; then ( sleep "${TIMEOUT:-120}"; kill $PID 2>/dev/null ) & fi
wait $PID || true
