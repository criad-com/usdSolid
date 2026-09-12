# SPDX-License-Identifier: MIT
"""Publish native closures and record verified cache hashes without local addresses."""
import json
import os
from pathlib import Path
import subprocess
from urllib.request import urlopen

from check_support import ROOT, check_built_revisions, runtime_paths


if __name__ == "__main__":
    runtime = Path(os.environ.get("USD_SOLID_RUNTIME", ROOT / "result-runtime")).resolve()
    paths = runtime_paths()
    dependencies = json.loads((ROOT / "dependencies.json").read_text())
    check_built_revisions(paths, dependencies)
    for role, name, manifest in (("schema", "usdSolid", ROOT / "library.json"),
                                 ("validators", "usdSolidValidators", ROOT / "nix/validators/library.json")):
        plugin, = json.loads((Path(paths[role]) / "lib" / name / "resources/plugInfo.json").read_text())["Plugins"]
        wanted = json.loads(manifest.read_text())
        if plugin["Info"]["aeco"] != {key: wanted[key] for key in ("version", "tier", "requires")}:
            raise RuntimeError("Build metadata does not match manifest: " + role)
    registry = json.loads(Path(os.environ["AECO_NIX_REGISTRY"]).read_text())
    endpoint = registry.get("cacheUrl") or next(
        url for url in registry["substituters"] if "cache.nixos.org" not in url)
    roots = {key: paths[key] for key in ("schema", "validators")}
    roots["runtime"] = str(runtime)
    print("== stage: publish native runtime closure", flush=True)
    subprocess.run(["attic", "push", "--jobs", "4", registry["cache"],
                    *roots.values()], check=True)
    closure = subprocess.check_output(
        ["nix-store", "--query", "--requisites", *roots.values()], text=True).splitlines()
    artifacts = {}
    print("== stage: verify published artifact hashes", flush=True)
    for role, store in roots.items():
        name = Path(store).name
        with urlopen(endpoint.rstrip("/") + "/" + name.split("-", 1)[0] + ".narinfo",
                     timeout=30) as response:
            fields = dict(line.split(": ", 1) for line in response.read().decode().splitlines()
                          if ": " in line)
        local_hash = subprocess.check_output(
            ["nix-store", "--query", "--hash", store], text=True).strip()
        remote_hash = subprocess.check_output(
            ["nix", "hash", "convert", "--hash-algo", "sha256", "--to", "nix32",
             fields["NarHash"]], text=True).strip()
        if fields["StorePath"] != store or "sha256:" + remote_hash != local_hash:
            raise RuntimeError("Cache artifact mismatch: " + role)
        artifacts[role] = {"store": name, "narHash": local_hash,
                           "narSize": int(fields["NarSize"])}
    receipt = {
        "version": json.loads((ROOT / "library.json").read_text())["version"],
        "revisions": paths["revisions"],
        "pushExitCode": 0,
        "closurePaths": len(set(closure)),
        "verifiedArtifacts": len(artifacts),
        "verification": "Recursive push succeeded; schema, validators and runtime cache StorePath and NarHash match the local build",
        "artifacts": artifacts,
    }
    (ROOT / "docs/cache-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Published {len(set(closure))} closure paths; verified {len(artifacts)} artifact hashes")
