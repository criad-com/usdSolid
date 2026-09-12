# SPDX-License-Identifier: MIT
"""Run Nix using an external deployment registry and the recorded revisions."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def arguments():
    registry = json.loads(Path(os.environ["AECO_NIX_REGISTRY"]).read_text())
    pins = json.loads((ROOT / "dependencies.json").read_text())["repos"]
    urls = {e["from"]["repo"]: "git+" + e["to"]["url"] for e in registry["flakes"]}
    args = ["--no-write-lock-file", "--max-jobs", "4", "--cores", "6",
            "--option", "substituters", " ".join(registry["substituters"])]
    for name in ("aeco-toolchain", "usdaeco-toolchain"):
        pin = pins[name]
        ref = pin["ref"]
        query = "ref=refs/tags/" + ref if ref.startswith("v") else "rev=" + ref
        args += ["--override-input", name, urls[name] + "?" + query]
    args += ["--override-input", "aeco-toolchain/openusd",
             urls["openusd"] + "?rev=47154dc7b5e28df623745495a7a508b69535ba24"]
    return args


if __name__ == "__main__":
    cli = sys.argv[1:]
    # Defaults precede user options and the command executed by `nix develop -c`.
    pos = 2 if cli[:1] == ["flake"] else 1
    raise SystemExit(subprocess.call(["nix", *cli[:pos], *arguments(), *cli[pos:]], cwd=ROOT))
