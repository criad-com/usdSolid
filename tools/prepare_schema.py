# SPDX-License-Identifier: MIT
"""Adapt GLOBAL build metadata only; preserve the upstream schema body verbatim."""
from pathlib import Path
import re
import sys


def prepare(path, name):
    path = Path(path)
    text = path.read_text()
    head, body = text.split('#************************************************************************************', 1)
    for key, value in (("libraryName", name), ("libraryPath", f"pxr/usd/{name}")):
        head, count = re.subn(r'(string ' + key + r'\s*=\s*)"[^"]*"',
                             lambda m: m[1] + '"' + value + '"', head)
        if count != 1:
            raise ValueError(f"expected exactly one GLOBAL.{key}")
    head = head.replace('    }\n', '        bool useLiteralIdentifier = true\n'
                        '        bool skipCodeGeneration = false\n    }\n', 1)
    path.write_text(head + '#************************************************************************************' + body)


if __name__ == "__main__":
    prepare(*sys.argv[1:])
