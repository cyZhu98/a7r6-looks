#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 cyZhu98
"""A7R6 Camera Raw profiles generated straight from the Sony look chain.

Base: 'SonyA7R6 Linear Base.dcp' - A7R6 Adobe Standard ColorMatrix1/2 (Adobe white balance),
ForwardMatrix = linear ProPhoto -> XYZ D50, identity tone curve.
Looks: XMP with RGBTable (ProPhoto primaries, gamma 1.8), table values = f_look(E^-1(v)) in display sRGB.

usage: acr_a7r6.py <st|fl2|all> [--grid 64] [--out DIR]
"""
import argparse
import base64
import hashlib
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # refcode/
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))

import crs_table as T                   # noqa: E402
import dcp                              # noqa: E402
import acr_encoding as E                # noqa: E402

import edit_binary as EB                # noqa: E402
import sony_look as SL                  # noqa: E402

SL.HUE_ATAN_TABLE = EB.va_of_file_offset(EB.HUE_ATAN_FILE)
SL.CONTRAST_FAMILY = EB.va_of_file_offset(EB.CONTRAST_FAMILY_FILE)

import sony_render as R                 # noqa: E402
import sony_sscs as SC                  # noqa: E402

ARW = r"D:\索尼\raw\2026年国庆北疆\DSC01352.ARW"
ADOBE_STD = Path(r"C:\ProgramData\Adobe\CameraRaw\CameraProfiles\Adobe Standard\Sony ILCE-7RM6 Adobe Standard.dcp")
MODEL = "Sony ILCE-7RM6"
BASE_NAME = "SonyA7R6 Linear Base"
GROUP = "Sony A7R6"
OUT = HERE / "out"
PROPHOTO_TO_XYZ = np.array([[0.7976749, 0.1351917, 0.0313534],
                            [0.2880402, 0.7118741, 0.0000857],
                            [0.0, 0.0, 0.8252100]])
PRIM_PROPHOTO, GAMMA_18 = 2, 2

LOOK_NAMES = {"st": "Standard", "vv": "Vivid", "nt": "Neutral", "pt": "Portrait", "fl": "FL",
              "vv2": "VV2", "in": "IN", "sh": "SH", "bw": "BW", "se": "Sepia",
              "fl2": "FL2", "fl3": "FL3"}

XYZ_TO_PROPHOTO = np.linalg.inv(PROPHOTO_TO_XYZ)
SRGB_TO_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                        [0.2126729, 0.7151522, 0.0721750],
                        [0.0193339, 0.1191920, 0.9503041]])
BRAD = np.array([[0.8951, 0.2664, -0.1614], [-0.7502, 1.7135, 0.0367], [0.0389, -0.0685, 1.0296]])
D65 = np.array([0.95047, 1.0, 1.08883]); D50 = np.array([0.96422, 1.0, 0.82521])
CHAD = np.linalg.inv(BRAD) @ np.diag((BRAD @ D50) / (BRAD @ D65)) @ BRAD
SRGB_TO_PROPHOTO = XYZ_TO_PROPHOTO @ CHAD @ SRGB_TO_XYZ


def srgb_dec(s):
    return np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)


def srgb_enc(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, 12.92 * l, 1.055 * l ** (1 / 2.4) - 0.055)


def srgb_to_prophoto_v(s):
    return np.clip(srgb_dec(s) @ SRGB_TO_PROPHOTO.T, 0, 1) ** (1 / 1.8)


def write_base():
    a = dcp.read(ADOBE_STD)
    ent = [("UniqueCameraModel", 2, MODEL), ("ProfileName", 2, BASE_NAME),
           ("ColorMatrix1", 10, a["ColorMatrix1"]), ("ColorMatrix2", 10, a["ColorMatrix2"]),
           ("CalibrationIlluminant1", 3, a["CalibrationIlluminant1"]),
           ("CalibrationIlluminant2", 3, a["CalibrationIlluminant2"]),
           ("ForwardMatrix1", 10, PROPHOTO_TO_XYZ), ("ForwardMatrix2", 10, PROPHOTO_TO_XYZ),
           ("ProfileToneCurve", 11, [0.0, 0.0, 1.0, 1.0]), ("ProfileEmbedPolicy", 4, [0]),
           ("DefaultBlackRender", 4, [1]), ("ProfileCopyright", 2, "a7r6-true-st (not an Adobe profile)")]
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{BASE_NAME}.dcp"
    dcp.write(path, ent)
    return path


def table_bytes(values, prim=PRIM_PROPHOTO, gamma=GAMMA_18):
    n = values.shape[0]
    ident = np.round(np.arange(n) * 65535 / (n - 1)).astype(np.int64)
    I = np.stack(np.meshgrid(ident, ident, ident, indexing="ij"), -1)
    q = np.round(np.clip(values, 0, 1) * 65535).astype(np.int64)
    body = ((q - I) % 65536).astype("<u2").tobytes()
    return (struct_pack(n) + body + struct_pack_num(prim, gamma) + np.array([0.0, 1.0], "<f8").tobytes())


def struct_pack(n):
    return struct.pack("<4I", 1, 1, 3, n)


def struct_pack_num(prim, gamma):
    return struct.pack("<3I", prim, gamma, 0)


XMP = """<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   crs:PresetType="Look"
   crs:Cluster=""
   crs:UUID="{uuid}"
   crs:SupportsAmount="False"
   crs:SupportsColor="True"
   crs:SupportsMonochrome="False"
   crs:SupportsHighDynamicRange="True"
   crs:SupportsNormalDynamicRange="True"
   crs:SupportsSceneReferred="True"
   crs:SupportsOutputReferred="False"
   crs:CameraModelRestriction="{model}"
   crs:Copyright=""
   crs:ContactInfo=""
   crs:Version="13.0"
   crs:ProcessVersion="11.0"
   crs:ConvertToGrayscale="False"
   crs:CameraProfile="{base}"
   crs:RGBTable="{md5}"
   crs:Table_{md5}="{table}"
   crs:HasSettings="True">
   <crs:Name>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{name}</rdf:li>
    </rdf:Alt>
   </crs:Name>
   <crs:ShortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:ShortName>
   <crs:SortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:SortName>
   <crs:Group>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{group}</rdf:li>
    </rdf:Alt>
   </crs:Group>
   <crs:Description>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:Description>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
"""


def write_look(tag, values):
    data = table_bytes(values)
    md5 = T.fingerprint(data)
    name = f"A7R6 {tag.upper()}"
    uuid = hashlib.md5(("A7R6/" + tag).encode()).hexdigest().upper()
    path = OUT / f"{name}.xmp"
    path.write_text(XMP.format(uuid=uuid, model=MODEL, base=BASE_NAME, md5=md5,
                               table=T.encode(data), name=name, group=GROUP), newline="\n")
    return path


def _calib():
    import json
    p = HERE / "calib.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    return np.array(d["gain"], np.float64), np.array(d["offset"], np.float64)


def build_values(look_name, n):
    looks = R.load_looks(ARW)
    sscs = SC.params_from_arw(ARW)
    look = R.Look(look_name, looks, sscs=sscs)
    g = np.arange(n) / (n - 1)
    grid = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
    lin = np.minimum(E.inverse(grid), E.CLIP)
    out = look.render(lin.reshape(-1, 1, 3), pointwise=True).reshape(-1, 3).astype(np.float64) / 16383.0
    out = np.clip(out, 0, 1)
    c = _calib()
    if c is not None:
        out = np.clip(out * c[0] + c[1], 0, 1)
    return np.clip(srgb_to_prophoto_v(out), 0, 1).reshape(n, n, n, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", nargs="?", default="st")
    ap.add_argument("--grid", type=int, default=64)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    global OUT
    if a.out:
        OUT = Path(a.out)
    print(write_base())
    targets = LOOK_NAMES if a.what == "all" else {a.what: LOOK_NAMES[a.what]}
    for tag, look_name in targets.items():
        v = build_values(look_name, a.grid)
        print(write_look(tag, v), f"({look_name})", flush=True)


if __name__ == "__main__":
    main()
