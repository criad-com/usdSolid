#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Native package acceptance using the family N checks, M failed contract."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from check_support import HEADINGS, check_pins, check_built_revisions, clean_env, run_native, runtime_paths


def main():
    try:
        paths = runtime_paths()
    except (OSError, ValueError):
        print("FAIL NativeRuntime — build .#runtime --out-link result-runtime first")
        print("1 checks, 1 failed")
        return 1
    kit = Path(os.environ.get("USDAECO_TOOLCHAIN_DIR", paths["toolchain"]))
    sys.path.insert(0, str(kit / "tools"))
    from usdaeco_check import Report
    from usdaeco_check.structure import check_structure

    report = Report()
    print("== stage: repository contracts", flush=True)
    # S02/S03 assume semantic repository names/headings. KitFlakeS05 keeps
    # S05's tag/version rules while allowing the external OpenUSD fork URLs.
    for result in check_structure(ROOT, only=["S01", "S04", "S25", "S26"]):
        report.add(result)
    readme = (ROOT / "README.md").read_text()
    report.check("KitReadme", re.findall(r"(?m)^## (.+)$", readme) == HEADINGS)
    manifest = json.loads((ROOT / "library.json").read_text())
    report.check("KitManifest", manifest == {"name": "usdSolid", "version": "0.1.5", "licence": "MIT",
                 "kind": "kit", "tier": "toolchain", "requires": {}})
    dependencies = json.loads((ROOT / "dependencies.json").read_text())
    report.run("KitFlakeS05", check_pins, dependencies,
               (ROOT / "flake.nix").read_text(), manifest["version"])
    report.run("BuiltRevisions", check_built_revisions, paths, dependencies)
    report.check("NoVendoredSchema", not list(ROOT.glob("usdSolid/schema.usda")))

    print("== stage: installed artifacts", flush=True)
    schema = Path(paths["schema"])
    validators = Path(paths["validators"])
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    report.check("SharedLibraries", all((p / "lib" / ("lib" + n + suffix)).is_file()
                 for p, n in ((schema, "usdSolid"), (validators, "usdSolidValidators"))))
    report.check("Resources", all((schema / "lib/usd/usdSolid/resources" / n).is_file()
                 for n in ("plugInfo.json", "schema.usda", "generatedSchema.usda")))
    report.check("PublicHeaders", len(list((schema / "include/pxr/usd/usdSolid").glob("*.h"))) >= 15)
    report.check("CmakeExports", all((p / "lib/cmake" / n / (n + "Config.cmake")).is_file()
                 for p, n in ((schema, "usdSolid"), (validators, "usdSolidValidators"))))
    upstream_schema = Path(paths["upstream"]) / "pxr/usd/usdSolid/schema.usda"
    installed_schema = schema / "lib/usdSolid/resources/usdSolid/schema.usda"
    report.check("SchemaBodyUnchanged", upstream_schema.read_text().split('#*****', 1)[1]
                 == installed_schema.read_text().split('#*****', 1)[1])
    report.check("UpstreamLicences", all(
        (p / "share/licenses" / n / "UPSTREAM-LICENSE.txt").read_bytes()
        == (Path(paths[up]) / "LICENSE.txt").read_bytes()
        for p, n, up in ((schema, "usdSolid", "upstream"),
                         (validators, "usdSolidValidators", "upstreamValidators"))))
    report.check("UpstreamDocumentation", (schema / "share/usdSolid/userDoc/overview.md").is_file())
    for prefix, name in ((schema, "usdSolid"), (validators, "usdSolidValidators")):
        plugin, = json.loads((prefix / "lib" / name / "resources/plugInfo.json").read_text())["Plugins"]
        wanted = manifest if name == "usdSolid" else json.loads((ROOT / "nix/validators/library.json").read_text())
        report.check(name + "Metadata", plugin["Type"] == "library" and plugin["Info"]["aeco"]
                     == {k: wanted[k] for k in ("version", "tier", "requires")})

    print("== stage: native runtime", flush=True)
    native = run_native(paths, "registry")
    report.check("RegistryClasses", len(native["classes"]) == 13, f'{len(native["classes"])} classes')
    report.check("PythonImport", native["python_import"])
    report.check("PythonAuthoring", native["authoring"])
    report.check("NativeValidators", len(native["validators"]) == 20, f'{len(native["validators"])} validators')
    report.check("OpenUsdVersion", native["openusd"] == [0, 26, 11])
    compatibility = dict(paths, plugins=os.pathsep.join(str(p / "lib/usd" / n / "resources")
                         for p, n in ((schema, "usdSolid"), (validators, "usdSolidValidators"))))
    report.check("CompatibilityDiscovery", run_native(compatibility, "registry") == native)
    for name, command in (
        ("UpstreamSchemaTests", [paths["python"], str(schema / "share/usdSolid/testenv/testUsdSolidBrepArray.py")]),
        ("UpstreamValidatorTests", [str(validators / "libexec/usdSolidValidators/testUsdSolidValidators")]),
    ):
        result = subprocess.run(command, env=clean_env(paths["plugins"]), capture_output=True, text=True, timeout=60)
        report.check(name, result.returncode == 0, (result.stderr or result.stdout).strip()[-500:])

    print("== stage: plugin-free composition", flush=True)
    result = subprocess.run([sys.executable, str(ROOT / "tools/vanilla_probe.py"),
                             str(ROOT / "testenv/vanilla.usda")], env=clean_env(),
                            capture_output=True, text=True, timeout=30)
    report.check("VanillaComposition", result.returncode == 0, (result.stdout or result.stderr).strip()[-500:])

    print("== stage: upstream fixture and CLI regression", flush=True)
    report.check("SeededBaCodes", len(run_native(paths, "seeded")) == 2,
                 "2 independent mutations: BA.010 and BA.020; CLI rejects both")
    actual = run_native(paths, "fixtures")
    expected = json.loads((ROOT / "testenv/expected/fixtures.json").read_text())
    report.check("FixtureFindings", actual == expected,
                 f'{actual["stages"]} stages, {actual["breps"]} Breps; '
                 f'{actual["error_free"]} error-free, {actual["with_errors"]} with errors; CLI agrees')
    if actual != expected:
        out = ROOT / "out"
        out.mkdir(exist_ok=True)
        (out / "fixtures.actual.json").write_text(json.dumps(actual, indent=2) + "\n")
    return report.finish()


if __name__ == "__main__":
    raise SystemExit(main())
