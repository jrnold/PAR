#!/usr/bin/env python3
"""Build the KEYS.DAT file that KEYS.COM types into a DOS session.

usage: mk.py OUT 'script'

Plain characters in the script are typed. Braces hold a named key or a timing command:

    {f1}..{f10} {enter} {esc} {tab} {bs} {del} {up} {down} {left} {right} {home} {end}
    {pgup} {pgdn}   named keys
    {w5}            wait 5 more seconds before the next key
    {d0.5}          set the default gap between keys to 0.5 seconds

KEYS.DAT is a list of 4-byte records: u16 timer ticks to wait, u8 ASCII code, u8 scancode.
"""

import re
import struct
import sys
from pathlib import Path

TICKS_PER_SECOND = 18.2065
SHIFTED = '~!@#$%^&*()_+{}|:"<>?'
UNSHIFTED = r"`1234567890-=[]\;',./"
ROW_STARTS = {2: "1234567890-=", 16: "qwertyuiop[]", 30: "asdfghjkl;'`", 44: "zxcvbnm,./"}
SCANCODES = {
    char: start + i for start, chars in ROW_STARTS.items() for i, char in enumerate(chars)
} | {"\\": 43, " ": 57}
NAMED_KEYS = {
    "enter": (13, 28),
    "esc": (27, 1),
    "tab": (9, 15),
    "bs": (8, 14),
    "up": (0, 72),
    "down": (0, 80),
    "left": (0, 75),
    "right": (0, 77),
    "home": (0, 71),
    "end": (0, 79),
    "del": (0, 83),
    "pgup": (0, 73),
    "pgdn": (0, 81),
} | {f"f{i}": (0, 58 + i) for i in range(1, 11)}


def ticks(seconds: float) -> int:
    """Convert seconds to BIOS timer ticks."""
    return round(seconds * TICKS_PER_SECOND)


def build(script: str) -> bytes:
    """Encode a key script as KEYS.DAT records."""
    out = b""
    gap = ticks(1.0)
    pending = gap
    for token in re.findall(r"\{[^}]*\}|.", script, re.DOTALL):
        if len(token) > 1 and token[0] == "{":
            name = token[1:-1]
            if re.fullmatch(r"w[\d.]+", name):
                pending += ticks(float(name[1:]))
                continue
            if re.fullmatch(r"d[\d.]+", name):
                gap = ticks(float(name[1:]))
                pending = gap
                continue
            ascii_code, scancode = NAMED_KEYS[name]
        else:
            base = UNSHIFTED[SHIFTED.index(token)] if token in SHIFTED else token
            ascii_code, scancode = ord(token), SCANCODES[base.lower()]
        out += struct.pack("<HBB", pending, ascii_code, scancode)
        pending = gap
    return out


if __name__ == "__main__":
    Path(sys.argv[1]).write_bytes(build(sys.argv[2]))
