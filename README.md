# usdSolid — boundary representation schemas for OpenUSD

## Purpose

Build the experimental UsdSolid schema as a separate native OpenUSD plugin,
with C++ interfaces and `pxr.UsdSolid` Python bindings. It carries boundary
representation data; geometry evaluation and tessellation belong to consumers.

## The schema on an index card

| Surface | Contents |
|---|---|
| Typed geometry | BrepArray, derived from Gprim |
| Geometry APIs | Point, four 3D curves, UV NURBS, six surfaces |
| Registry | 13 classes, prefix UsdSolid |
| Validators | Separate native package, 20 validators with BA rule codes |

## Build

```sh
nix build .#usdSolid .#usdSolidValidators --max-jobs 4 --cores 6
nix build .#runtime --out-link result-runtime --max-jobs 4 --cores 6
nix develop --max-jobs 4 --cores 6
env -u PYTHONPATH python -c 'from pxr import UsdSolid; print(UsdSolid.BrepArray)'
env -u PYTHONPATH python check.py
env -u PYTHONPATH python -m pytest -q
nix flake check --max-jobs 4 --cores 6
```

Family inputs use the public [criad-com organization](https://github.com/criad-com)
and have deployment overrides in the external `AECO_NIX_REGISTRY` JSON.
For a checkout using that registry:

```sh
export PYTHON=python3
export AECO_NIX_REGISTRY="$HOME/.config/aeco/nix-registry.json"
env -u PYTHONPATH "$PYTHON" tools/nix_local.py build .#runtime --out-link result-runtime
env -u PYTHONPATH "$PYTHON" tools/nix_local.py develop
```

The helper uses the recorded revisions and limits builds to four jobs and
six cores. The same helper accepts `flake check`. No editable Python install
is required. Outside the shell, `check.py` uses `result-runtime/paths.json`
to start native probes in the correct Python ABI, while the invoking Python
runs the plugin-free probe. Source tests add `tools/` through conftest.py.

The runtime's JSON also gives the installed `fixtures` directory. To inspect
one of its stages inside the shell:

```sh
export SOLID_FIXTURES="$(env -u PYTHONPATH python -c 'import json,os; print(json.load(open(os.environ["USD_SOLID_RUNTIME"]+"/paths.json"))["fixtures"])')"
usdchecker --includeKeywords UsdSolidValidators "$SOLID_FIXTURES/testProducerCube.usda"
```

To publish the built closures to the configured binary cache:

```sh
env -u PYTHONPATH "$PYTHON" tools/push_cache.py
```

## Upstream pin

Schema revision `1f6d6d31f1cbeed452b4e1c312bf974d0519d71d`;
validator revision `152c37a46c8cb71fbe1363772f1ccffe6e91c78b`.
See [upstream sources, classes and adaptations](docs/upstream.md).

## Layout

- `nix/`: library-name selection and native CMake packaging.
- `tools/`: build preparation and local input resolution.
- `testenv/`: package discovery and binding tests.
- `docs/upstream.md`: source provenance and deviations.

Upstream sources are copied into derivation work directories at build time.
Generated files are build artifacts.
The install provides `lib/libusdSolid.dylib`, public headers and CMake
targets, `lib/usdSolid/resources`, the compatibility path
`lib/usd/usdSolid/resources`, and `pxr/UsdSolid` in Python site-packages.
Linux uses `.so` libraries.

## Status

Version 0.1.4 pins usdaeco-toolchain v0.3.9, fixing the builder's Nix package
version metadata. Family public names remain `github.com/criad-com`.
All other dependency pins are unchanged.
Source pytest has **8 passing tests**; the three applicable shared structure
checks pass with v0.3.9. Native rebuild and receipt regeneration are pending
review; neither the native build nor `nix flake check` was attempted for this
update. The prior [blocker record](BLOCKED.md) is retained unchanged.
The previous gate run against the existing v0.1.2 runtime reported
**28 checks, 3 failed**:
the built toolchain revision and both installed plugin versions are stale.
The other 25 checks pass, including 13 registered classes, 20 validators,
17 upstream Python tests, the native validator test and plugin-free composition.
The fixture corpus remains **40 stages / 50 Breps**: 35 stages are error-free;
five produce 28 errors. Registry and CLI findings agree for all 40 stages.
These are regression measurements of v0.1.2; native v0.1.4 acceptance is
**not proven**. The [cache receipt](docs/cache-receipt.json) records the new
requested toolchain revision and is marked pending; its artifacts and
publication counts remain historical v0.1.2 evidence.
See [the verification record](docs/verification.md).

The five P2 examples and 66 producer defect fixtures remain absent from the
pins and not proven. See [the measured deviations](docs/upstream.md#fixture-availability).
Upstream `CanApply` declarations also raise an unknown-type error in the
existing runtime; direct `Apply` and authoring work. This limitation is
preserved and documented with the upstream pin.

Without the plugin, a BrepArray stage opens and preserves authored data,
but its prim has no recognized schema type. The authored `BrepArray` token
remains; no `fallbackPrimTypes` is added. This is expected degradation,
and does not provide a renderable body. Applications supply a Mesh twin.

## Licence

Packaging: [MIT](LICENSE); upstream files retain
[TOST 1.0 (Tomorrow Open Source Technology License 1.0)](docs/upstream.md#licence),
installed verbatim with each package.
