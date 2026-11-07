# Quattro Pro 4 in Docker

Borland Quattro Pro 4.0 for DOS, running under DOSBox-X in a Docker image. Use it to open the
`.WQ!` spreadsheets from the PAR diskettes, for example to export a sheet that `sqz` can't read.

The image downloads Quattro Pro from WinWorld while it builds, so it contains copyrighted
software. Keep it local and never push it to a public registry.

## Build

```sh
docker build -t qp4 quattro-pro-4/
```

The build runs `setup.sh`, which checks the download against a SHA-256, unpacks the two floppy
images, and drives `INSTALL.EXE` inside DOSBox-X with `KEYS.COM` feeding the keystrokes. It takes a
few minutes. To use a different download, set `QP4_SHA256` in the build.

## Run

The container has no native window. Docker Desktop on macOS can't show one, so there are two modes.

**In a browser.** DOSBox-X runs on a virtual display that is served through VNC and noVNC:

```sh
docker run -d --name qp4-gui -e GUI=1 -p 127.0.0.1:6080:6080 \
  -v "$PWD/sheets:/work" qp4 'Q BERNDT.WQ!'
docker logs qp4-gui    # prints the URL and a random VNC password
```

Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale> and enter the password. Each start
generates a new one. Always publish the port on `127.0.0.1`. Quitting Quattro Pro ends the
container. Remove it with `docker rm -f qp4-gui`.

**Headless.** Feed in keystrokes and save screenshots:

```sh
docker run --rm -e KEYS='{w5}/fr{enter}' -e SHOT_AT='8' -v "$PWD/sheets:/work" qp4
```

The screenshots land in the mounted folder as `shot-<seconds>.png`.

## Files

The host folder you mount at `/work` appears in DOS as `C:\WORK`, and the program starts there.
Quattro Pro writes backup and temporary files next to what it opens, so mount a copy of the
spreadsheets, not `data/raw/`.

Each argument after the image name is one DOS command, run from `C:\QPRO`. The default is `Q`.
`Q BERNDT.WQ!` opens a file at start. Inside Quattro Pro, `/File Retrieve` (`/fr`) opens others.

## Environment variables

  | Variable  | Meaning                                                                             |
  | --------- | ----------------------------------------------------------------------------------- |
  | `GUI`     | Set to `1` to serve the display on port 6080 with a password.                       |
  | `KEYS`    | Keystrokes to type after start, in the `mk.py` syntax (`{w5}`, `{enter}`, `{f10}`). |
  | `SHOT_AT` | Space-separated seconds after start at which to save `/work/shot-<s>.png`.          |
  | `TIMEOUT` | Kill DOSBox-X after this many seconds. Default 120, or never with `GUI`.            |

## Files in this folder

  | File            | Purpose                                                                                                                 |
  | --------------- | ----------------------------------------------------------------------------------------------------------------------- |
  | `Dockerfile`    | Installs the tools, runs `setup.sh`, and adds the VNC packages.                                                         |
  | `setup.sh`      | Downloads, verifies and installs Quattro Pro under DOSBox-X. Embeds the 213-byte `KEYS.COM` keystroke feeder as base64. |
  | `entrypoint.sh` | Writes the DOSBox-X config, starts the display, and runs the commands.                                                  |
  | `mk.py`         | Builds the `KEYS.DAT` file that `KEYS.COM` types into the session.                                                      |
