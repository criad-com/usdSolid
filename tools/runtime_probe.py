# SPDX-License-Identifier: MIT
"""Run inside the Python ABI used to compile the native plugins."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def registry(paths):
    # Deliberately import UsdSolid before UsdGeom to exercise initialization.
    from pxr import UsdSolid, Plug, Tf, Usd, UsdGeom, UsdValidation
    document = json.loads((Path(paths["schema"]) / "lib/usdSolid/resources/plugInfo.json").read_text())
    types = sorted(document["Plugins"][0]["Info"]["Types"])
    plugin = Plug.Registry().GetPluginWithName("usdSolid")
    assert plugin and plugin.Load()
    for name in types:
        typ = Tf.Type.FindByName(name)
        assert typ and Plug.Registry().GetPluginForType(typ) == plugin
        assert getattr(UsdSolid, name.removeprefix("UsdSolid"))._GetStaticTfType() == typ
    stage = Usd.Stage.CreateInMemory()
    brep = UsdSolid.BrepArray.Define(stage, "/Body")
    brep.CreateBrepRegionCountAttr([2])
    assert list(brep.GetBrepRegionCountAttr().Get()) == [2]
    assert brep.GetPrim().IsA(UsdGeom.Gprim)
    vr = UsdValidation.ValidationRegistry()
    metadata = vr.GetValidatorMetadataForKeyword("UsdSolidValidators")
    validators = [vr.GetOrLoadValidatorByName(m.name) for m in metadata]
    assert all(validators)
    assert all("UsdSolidBrepArray" in m.GetSchemaTypes() for m in metadata)
    return {"classes": types, "validators": sorted(m.name for m in metadata),
            "authoring": True, "python_import": True, "openusd": list(Usd.GetVersion())}


def fixtures(paths):
    from pxr import Usd, UsdValidation
    vr = UsdValidation.ValidationRegistry()
    metadata = vr.GetValidatorMetadataForKeyword("UsdSolidValidators")
    validators = [vr.GetOrLoadValidatorByName(m.name) for m in metadata]
    assert len(validators) == 20 and all(validators)
    context = UsdValidation.ValidationContext(validators)
    root = Path(paths["fixtures"])
    rows = []
    for path in sorted(root.rglob("*.usda")):
        stage = Usd.Stage.Open(str(path))
        assert stage and not stage.GetCompositionErrors(), path.name
        breps = [p for p in stage.Traverse() if p.GetTypeName() == "BrepArray"]
        assert breps, path.name
        errors = context.Validate(stage)
        counts = Counter()
        codes = set()
        for e in errors:
            severity = "error" if e.GetType() == UsdValidation.ValidationErrorType.Error else "warning"
            ba = re.findall(r"BA\.\d+", e.GetMessage())
            codes.update(ba)
            counts[(severity, e.GetIdentifier(), tuple(ba))] += 1
        cli = subprocess.run([paths["checker"], "--includeKeywords", "UsdSolidValidators",
                              str(path)], capture_output=True, text=True, timeout=30)
        cli_codes = set(re.findall(r"BA\.\d+", cli.stdout + cli.stderr))
        error_count = sum(v for (severity, _, _), v in counts.items() if severity == "error")
        assert cli.returncode == (1 if error_count else 0), (path.name, cli.returncode)
        assert cli_codes == codes, (path.name, cli_codes, codes)
        rows.append({"file": path.relative_to(root).as_posix(), "breps": len(breps),
                     "errors": error_count, "warnings": len(errors) - error_count,
                     "cli_exit": cli.returncode,
                     "findings": [{"severity": severity, "identifier": identifier,
                                   "codes": list(ba), "count": count}
                                  for (severity, identifier, ba), count in sorted(counts.items())]})
    return {"stages": len(rows), "breps": sum(r["breps"] for r in rows),
            "error_free": sum(r["errors"] == 0 for r in rows),
            "with_errors": sum(r["errors"] > 0 for r in rows), "fixtures": rows}


def seeded(paths):
    from pxr import Usd, UsdValidation
    vr = UsdValidation.ValidationRegistry()
    metadata = vr.GetValidatorMetadataForKeyword("UsdSolidValidators")
    context = UsdValidation.ValidationContext([vr.GetOrLoadValidatorByName(m.name) for m in metadata])
    rows = []
    for attribute, value, expected in (("brep:intersectTol3d", [-1.0], "BA.010"),
                                        ("brep:extent", [], "BA.020")):
        stage = Usd.Stage.Open(str(Path(paths["fixtures"]) / "testProducerCube.usda"))
        assert not context.Validate(stage)
        stage.SetEditTarget(stage.GetSessionLayer())
        prim = next(p for p in stage.Traverse() if p.GetTypeName() == "BrepArray")
        prim.GetAttribute(attribute).Set(value)
        errors = context.Validate(stage)
        codes = set(code for e in errors for code in re.findall(r"BA\.\d+", e.GetMessage()))
        assert expected in codes
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "defect.usda"
            stage.Flatten().Export(str(path))
            cli = subprocess.run([paths["checker"], "--includeKeywords", "UsdSolidValidators", str(path)],
                                 capture_output=True, text=True, timeout=30)
            assert cli.returncode == 1 and expected in cli.stdout + cli.stderr
        rows.append({"attribute": attribute, "expected": expected, "cli_exit": 1})
    return rows


if __name__ == "__main__":
    print(json.dumps(globals()[sys.argv[1]](json.loads(sys.argv[2])), sort_keys=True))
