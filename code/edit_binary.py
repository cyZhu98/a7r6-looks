# SPDX-License-Identifier: MIT
# Derived from 751K/sony-a7m5-looks (sonylook/edit_binary.py), adapted for the Windows PE
# build of Imaging Edge Edit. Original copyright (c) 2026 sony-a7m5-looks contributors;
# modifications copyright (c) 2026 cyZhu98. Licensed under the MIT License.
# See ../THIRD-PARTY.md
"""Windows PE variant of edit_binary: read constant tables from the user's own Imaging Edge Edit.

Confirmed tables in Edit.exe 4.1.01.06121 (x86-64):
  atan  float32[512]   file 0x46E598
  family int32[37][1025] file 0x48C200 (row 18 = identity, 64*i clamped)
File offset -> RVA uses the section table, so addresses below are VAs (image base 0x140000000).
"""
import os
import struct
from functools import lru_cache
from pathlib import Path

DEFAULT = r"A:\Apps\SonyIE\Edit.exe"
RESOURCES = r"A:\Apps\SonyIE"


def binary_path():
    return Path(os.environ.get("SONY_EDIT_BINARY", DEFAULT))


def resources_path():
    return Path(os.environ.get("SONY_EDIT_RESOURCES", RESOURCES))


@lru_cache(maxsize=1)
def _image():
    data = binary_path().read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[pe:pe + 4] == b"PE\0\0", "not a PE image"
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    magic = struct.unpack_from("<H", data, pe + 24)[0]
    if magic == 0x20B:
        base = struct.unpack_from("<Q", data, pe + 24 + 24)[0]
    else:
        base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    off, segs = pe + 24 + optsz, []
    for _ in range(nsec):
        name = data[off:off + 8].rstrip(b"\0").decode()
        vsize, va, rawsize, rawoff = struct.unpack_from("<IIII", data, off + 8)
        segs.append((name, base + va, vsize, rawoff, rawsize))
        off += 40
    return data, segs, base


@lru_cache(maxsize=1)
def segments():
    _, segs, _ = _image()
    return segs


def read_va(va, n):
    data, segs, _ = _image()
    for name, seg_va, vsize, rawoff, rawsize in segs:
        if seg_va <= va and va + n <= seg_va + rawsize:
            o = rawoff + (va - seg_va)
            return data[o:o + n]
    raise ValueError(f"0x{va:x}+{n} is not file-backed")


def read_off(off, n):
    return _image()[0][off:off + n]


def va_of_file_offset(off):
    data, segs, _ = _image()
    for name, seg_va, vsize, rawoff, rawsize in segs:
        if rawoff <= off < rawoff + rawsize:
            return seg_va + (off - rawoff)
    raise ValueError(hex(off))


# file offsets located by scanning this build
HUE_ATAN_FILE = 0x46E598
CONTRAST_FAMILY_FILE = 0x48C200


def arm64_slice():
    """Compatibility shim: the whole image, used only as a cache key / SHA."""
    return _image()[0]
