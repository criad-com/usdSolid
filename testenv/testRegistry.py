#!/pxrpythonsubst
# SPDX-License-Identifier: MIT
"""Smoke the generated C++ library, Python wrapper, and registered schemas."""
from pxr import Plug, Tf, Usd, UsdGeom, UsdSolid

CLASSES = (
    "BrepArray", "BrepPointAPI", "BrepCurve3dNurbAPI", "BrepCurve3dLineAPI",
    "BrepCurve3dCircleAPI", "BrepCurve3dEllipseAPI", "BrepCurveUvNurbAPI",
    "BrepSurfaceNurbAPI", "BrepSurfaceSphereAPI", "BrepSurfacePlaneAPI",
    "BrepSurfaceCylinderAPI", "BrepSurfaceConeAPI", "BrepSurfaceTorusAPI",
)


def probe():
    registry = Plug.Registry()
    plugin = registry.GetPluginWithName("usdSolid")
    assert plugin and plugin.Load()
    for name in CLASSES:
        cls = getattr(UsdSolid, name)
        typ = Tf.Type.FindByName("UsdSolid" + name)
        assert typ and registry.GetPluginForType(typ) == plugin, name
        assert cls._GetStaticTfType() == typ, name
    stage = Usd.Stage.CreateInMemory()
    brep = UsdSolid.BrepArray.Define(stage, "/Body")
    assert brep and brep.GetPrim().IsA(UsdGeom.Gprim)
    brep.CreateBrepRegionCountAttr([2])
    assert list(brep.GetBrepRegionCountAttr().Get()) == [2]
    print("13 classes registered; Python import and authoring passed")


if __name__ == "__main__":
    probe()
