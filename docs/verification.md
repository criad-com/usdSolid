# Verification record

## v0.1.4 toolchain re-pin

The toolchain pin is v0.3.9, revision
`d8f09dfd2ddfb6e8a08a9528e90f949248d5a1c2`. This release fixes the
toolchain's Nix package version metadata. The other four dependency entries
are unchanged, and family inputs retain `github:criad-com/` public names.

| Acceptance | Result |
|---|---|
| Packaging metadata | Version 0.1.4 in both manifests, CMake projects, pyproject.toml and the gate |
| Changed dependency pins | 1: usdaeco-toolchain v0.3.9; other 4 entries unchanged |
| Shared structure lint | 3 checks, 0 failed: S01, S25, S26 from the pinned v0.3.9 checkout |
| Source pytest | 8 passed |
| Public-name sweep | 0 old public references in tracked repository files |
| Superseded toolchain pin sweep | 0 superseded tag or revision references in tracked repository files |
| Whitespace | `git diff --check` clean |
| Native rebuild / check.py / nix flake check | Not run for this update; native acceptance not proven |
| Cache receipt | Requested toolchain revision updated; marked pending native rebuild and regeneration; v0.1.2 artifacts and publication counts retained |
| Blocker record | `BLOCKED.md` retained byte-for-byte |

### Deviations

Native rebuild, full acceptance, cache publication and receipt regeneration
are deferred to review. The receipt's toolchain revision is the requested
source pin, not verified build provenance; its explicit pending status and
verification text distinguish that pin from the historical v0.1.2 artifacts.
The [prior blocker record](../BLOCKED.md) is unchanged. No native or flake
check attempt was made for this update.

## Historical v0.1.3 public-name update

These measurements used the then-pinned shared structure lint and the
existing v0.1.2 runtime. They do not establish native v0.1.4 acceptance.

| Acceptance | Result |
|---|---|
| Public-name sweep | 0 old public references in tracked repository files |
| Packaging metadata | Version 0.1.3 in both manifests, CMake projects, pyproject.toml and the gate |
| Changed dependency pins | 1: usdaeco-toolchain; other 4 entries unchanged |
| Shared structure lint | 3 checks, 0 failed: S01, S25, S26 |
| Source pytest | 8 passed |
| Native build through registry helper | Stopped after Nix planned 1,116 derivations and began fetching bootstrap sources outside the permitted network scope |
| check.py against v0.1.2 runtime | 28 checks, 3 failed: BuiltRevisions, usdSolidMetadata, usdSolidValidatorsMetadata |
| Runtime regression | 13 classes, 20 validators, 17 upstream Python tests and native validator executable pass |
| Upstream licence preservation | Both installed licence files byte-identical to pinned sources |
| Fixture regression | 40 stages / 50 Breps; 35 error-free, 5 with errors; 28 errors and 5 warnings; registry and CLI agree |
| Plugin-free composition / seeded defects | Pass / BA.010 and BA.020 rejected |
| nix flake check | 1 attempt, exit 1; native outputs evaluate; missing build dependency with local builds disabled |
| Cache receipt | Existing v0.1.2 receipt retained unchanged; v0.1.3 closure not built or published |
| Example results | No republish; no result manifest embeds the changed public names |

The flake-check attempt used the external-registry helper with `--offline
--max-jobs 0 --option substituters '' --option extra-substituters ''` to avoid
further source downloads. It stopped at the missing `m4-1.4.21.tar.bz2`
derivation. This establishes evaluation, not successful native acceptance.
The full flake command was not retried.

At that point the cache receipt remained unchanged evidence for v0.1.2.
The current receipt status and required regeneration are recorded above.

## Historical v0.1.0 measurements

Measured on aarch64-darwin.

| Acceptance | Result |
|---|---|
| Native schema and validator builds | PASS; 3 CTest entries in total |
| Generated schema registry | PASS; 13 classes |
| Development-shell Python import | PASS; pxr.UsdSolid.BrepArray |
| Installed upstream Python tests | PASS; 17 tests |
| Native validator registry | PASS; 20 validators |
| Upstream C++ validator executable | PASS |
| Canonical and compatibility resource discovery | PASS; fresh processes |
| Plugin-free composition | PASS; authored data retained, no recognized typed schema |
| Fork fixture stages / BrepArray prims | 40 / 50; all compose |
| Error-free fixture stages | 35; CLI exit 0 |
| Fixture stages with errors | 5; 28 errors in total; CLI exit 1 |
| Fixture warnings | 5 across 3 stages |
| Registry / usdchecker agreement | 40 of 40 stages |
| Independently seeded defects | 2; BA.010 and BA.020, both rejected by CLI |
| P2 stages / producer defect corpus | Not present; 5 / 66 acceptance not proven |
| check.py | 28 checks, 0 failed, 0 not run |
| Source pytest | 8 passed |
| Nix acceptance derivation after pin correction | PASS; same 28 checks and 8 tests |
| Full nix flake check | One attempt; failed annotated-tag bookkeeping, corrected afterward |
| Linux | Validator derivation evaluates; native build not run |
| Binary cache | 12 paths uploaded, including schema, validators and runtime closures |
| Shared structure lint | S01, S25, S26 pass; explicit kit checks replace semantic assumptions |

The full flake command was not retried. The corrected Nix gate was built with
`nix build .#checks.aarch64-darwin.acceptance`, using the local input helper.
The [deviations](upstream.md#deviations) cover the applicability error,
resource compatibility layout, source availability and upstream findings.

The cache command is `python tools/push_cache.py`; it delegates to `attic push`
with the cache name read from the external `AECO_NIX_REGISTRY` JSON.
The uploaded native store basenames are:

- `rbq7nn1bgnpna50ki2i46ilkzc4mybiy-usdSolid-0.1.0`
- `mq09z4rpgqdj21j280465f9bi28bx5vf-usdSolidValidators-0.1.0`
- `ip654m2zx2bh1lf62k3y1hr69mwhfyk9-usdSolid-runtime`
