# SPDX-License-Identifier: MIT
"""Adapt the upstream plugin descriptor to the native install contract."""
import json
from pathlib import Path
import sys


def prepare(source, target):
    document = json.loads(Path(source).read_text())
    plugin, = document["Plugins"]
    assert plugin["Name"] == "usdSolidValidators"
    assert len([k for k in plugin["Info"]["Validators"] if k != "keywords"]) == 20
    plugin.update(Root="..", ResourcePath="resources",
                  LibraryPath="../@CMAKE_SHARED_LIBRARY_PREFIX@usdSolidValidators@CMAKE_SHARED_LIBRARY_SUFFIX@")
    text = json.dumps(document, indent=2)
    # Let the CMake helper supply authoritative version and requirement ranges.
    text = text.replace('"Info": {', '"Info": {\n        "aeco": @AECO_METADATA@,', 1)
    Path(target).write_text(text + "\n")


if __name__ == "__main__":
    prepare(*sys.argv[1:])
