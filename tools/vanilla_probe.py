# SPDX-License-Identifier: MIT
"""Composition-only degradation test; this is not a valid solid fixture."""
from pathlib import Path
import sys
from pxr import Plug, Usd

assert not Plug.Registry().GetPluginWithName("usdSolid")
stage = Usd.Stage.Open(str(Path(sys.argv[1])))
assert stage and not stage.GetCompositionErrors()
assert not stage.GetMetadata("fallbackPrimTypes")
prim = stage.GetPrimAtPath("/Body")
assert prim and prim.GetTypeName() == "BrepArray"
assert not prim.IsA(Usd.Typed)
assert list(prim.GetAttribute("brep:regionCount").Get()) == [2]
print("stage opens; authored data retained; prim has no recognized typed schema")
