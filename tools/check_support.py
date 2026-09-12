# SPDX-License-Identifier: MIT
"""Shared source and subprocess checks; no installed package required."""
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = ["Purpose", "The schema on an index card", "Build", "Upstream pin",
            "Layout", "Status", "Licence"]


def check_pins(document, flake, version):
    """Kit S05: family tags and version agreement, plus external fork revisions."""
    flake = re.sub(r"(?m)^\s*#.*$", "", flake)
    for literal in re.findall(r'\bversion\s*=\s*"([^"]*)"\s*;', flake):
        assert "${" in literal or literal == version, "Flake version differs from library.json"
    urls = re.findall(r'url = "github:([^/]+)/([^?]+)\?(ref|rev)=([^"]+)"', flake)
    pins = document["repos"]
    assert len(urls) == len(pins) == 5
    expected = [("criad-com" if name in ("aeco-toolchain", "usdaeco-toolchain")
                 else "jensjebens", pin["repo"], pin["ref"]) for name, pin in pins.items()]
    assert sorted((owner, repo, ref) for owner, repo, _, ref in urls) == sorted(expected)
    assert all(re.fullmatch(r"v\d+\.\d+\.\d+|[a-f0-9]{40}", p["ref"]) for p in pins.values())
    for name in ("aeco-toolchain", "usdaeco-toolchain"):
        pin = pins[name]
        assert re.fullmatch(r"v\d+\.\d+\.\d+", pin["ref"]), "Family inputs require release tags"
        assert ("criad-com", pin["repo"], "ref", pin["ref"]) in urls
        assert re.fullmatch(r"[a-f0-9]{40}", pin.get("revision", "")), "Record checked revision"
    assert 'nixpkgs.follows = "aeco-toolchain/nixpkgs"' in flake
    assert 'usdaeco-toolchain.flake = false;' in flake
    assert 'usdaeco-toolchain.inputs.' not in flake
    return True


def check_built_revisions(paths, document):
    """Accept checked forge or public orphan commits, never arbitrary revisions."""
    revisions = paths.get("revisions", {})
    pins = document["repos"]
    assert revisions.keys() == pins.keys(), "Build input inventory differs from pins"
    for name, pin in pins.items():
        allowed = {pin.get("revision", pin["ref"])}
        if "publicRevision" in pin:
            allowed.add(pin["publicRevision"])
        assert revisions[name] in allowed, "Build revision differs from pins: " + name
    return True


def runtime_paths():
    directory = Path(os.environ.get("USD_SOLID_RUNTIME", ROOT / "result-runtime"))
    return json.loads((directory / "paths.json").read_text())


def clean_env(plugins=None):
    env = dict(os.environ)
    for key in ("PYTHONPATH", "PXR_PLUGINPATH_NAME", "PXR_AR_DEFAULT_SEARCH_PATH"):
        env.pop(key, None)
    if plugins is not None:
        env["PXR_PLUGINPATH_NAME"] = str(plugins)
    return env


def run_native(paths, mode):
    result = subprocess.run([paths["python"], str(ROOT / "tools/runtime_probe.py"), mode,
                             json.dumps(paths)], env=clean_env(paths["plugins"]),
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:] or result.stdout[-3000:])
    return json.loads(result.stdout)
