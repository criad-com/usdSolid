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
with release-tag refs: **aeco-toolchain v0.4.0** and
**usdaeco-toolchain v0.3.10**. The latter is a non-recursive source input;
the flake imports its builders without resolving its own test fixtures.
Deployment overrides live in the external `AECO_NIX_REGISTRY` JSON.
For a checkout using that registry:

```sh
export PYTHON=python3
export AECO_NIX_REGISTRY="$HOME/.config/aeco/nix-registry.json"
env -u PYTHONPATH "$PYTHON" tools/nix_local.py build .#runtime --out-link result-runtime
env -u PYTHONPATH "$PYTHON" tools/nix_local.py develop
```

The helper selects the recorded release tags and limits builds to four jobs and
six cores. The same helper accepts `flake check`. No editable Python install
is required. Outside the shell, `check.py` uses `result-runtime/paths.json`
to start native probes in the correct Python ABI, while the invoking Python
runs the plugin-free probe. Source tests add `tools/` through conftest.py.

For offline checks, set `AECO_TOOLCHAIN_ROOT` and `USDAECO_TOOLCHAIN_ROOT`
to existing checkouts containing the pinned tags, then use:

```sh
nix flake check --offline --no-write-lock-file \
  --override-input aeco-toolchain "git+file://$AECO_TOOLCHAIN_ROOT?ref=refs/tags/v0.4.0" \
  --override-input usdaeco-toolchain "git+file://$USDAECO_TOOLCHAIN_ROOT?ref=refs/tags/v0.3.10"
```

Offline source resolution still requires cached transitive inputs and build
dependencies. The v0.1.5 release receipt records 78 published closure paths
and three verified artifacts; its existing runtime passes all 29 gate checks.

`dependencies.json` records the checked forge commits as `revision` and the
independent public release commits as `publicRevision`. Native provenance
checks accept either recorded commit; cache receipts always record the
actual fetched revisions.

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

Version **0.1.6** updates the release documentation and retains the two
published toolchain tags above. Both tags were verified on GitHub and the
forge; the three external OpenUSD source pins and all requirement ranges
are unchanged.

Source pytest has **16 passing tests**. Shared structure rules S01, S04,
S25 and S26 pass with toolchain v0.3.10; the kit's S05 equivalent checks
family release tags and flake version agreement while retaining the
external fork URLs.

The published v0.1.5 runtime passes **29 checks, 0 failed, 0 not run**,
including 13 classes, 20 validators, 17 upstream Python tests, the native
validator test, plugin-free composition and the **40-stage / 50-Brep**
fixture findings. The [cache receipt](docs/cache-receipt.json) records its
successful publication: 78 closure paths and three verified artifact hashes.
These results supersede the initial v0.1.5 attempt using stale v0.1.4 artifacts.

The v0.1.6 patch has source validation only; its native acceptance is
**not proven** until the reviewer rebuilds and regenerates the receipt.
See [the verification record](docs/verification.md) for the release evidence
and historical gate results.

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
