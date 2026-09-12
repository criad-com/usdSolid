# Upstream source and packaging boundary

The schema is pinned to [the schema branch, PR 61](https://github.com/jensjebens/OpenUSD/pull/61)
at revision `1f6d6d31f1cbeed452b4e1c312bf974d0519d71d`.
Its source path is `pxr/usd/usdSolid/schema.usda`; its GLOBAL libraryName is
`usdSolid`, libraryPrefix and tokensPrefix are `UsdSolid`.

The separate [validator branch, PR 67](https://github.com/jensjebens/OpenUSD/pull/67)
is pinned at `152c37a46c8cb71fbe1363772f1ccffe6e91c78b`, path
`pxr/usdValidation/usdSolidValidators`. It contains 20 native validators.
The schema on that branch differs from the schema pin only in documentation
about cone and UV parameterization. Each branch is a revision-pinned,
non-flake input. No upstream schema, generated C++, validator source or
fixture is copied into this repository.

| Schema class | Kind |
|---|---|
| BrepArray | Concrete typed, inherits Gprim |
| BrepPointAPI | Multiple apply |
| BrepCurve3dNurbAPI | Multiple apply |
| BrepCurve3dLineAPI | Multiple apply |
| BrepCurve3dCircleAPI | Multiple apply |
| BrepCurve3dEllipseAPI | Multiple apply |
| BrepCurveUvNurbAPI | Single apply |
| BrepSurfaceNurbAPI | Single apply |
| BrepSurfaceSphereAPI | Single apply |
| BrepSurfacePlaneAPI | Single apply |
| BrepSurfaceCylinderAPI | Single apply |
| BrepSurfaceConeAPI | Single apply |
| BrepSurfaceTorusAPI | Single apply |

The registered C++ names prepend `UsdSolid` to these 13 identifiers. Python
exposes them in `pxr.UsdSolid`; stages use `BrepArray` and the API identifiers.

## Build adaptations

`nix/library-name.nix` selects the package library name. During unpack, the
derivation copies schema.usda, module.cpp, __init__.py, userDoc, testenv and
examples if present. `tools/prepare_schema.py` changes only GLOBAL build
metadata: the selected libraryName, the C++ include path `pxr/usd/usdSolid`
(upstream has `./`), and explicit `useLiteralIdentifier = true` and
`skipCodeGeneration = false`. Everything after GLOBAL remains verbatim.
The shared builder runs usdGenSchema and its validation pass against the
pinned development OpenUSD, then compiles fresh C++ and Python bindings.
The built Python initializer imports UsdGeom before loading UsdSolid, so
the base-class wrappers exist even when UsdSolid is imported first.

The build uses the toolchain's out-of-tree CMake contract and separate
native validator package. It does not add geometry, identity, classification
or spatial structure to the AECO core. Exact geometry evaluation and
tessellation are separate consumers.

## Licence

The upstream `LICENSE.txt` begins with the following notice, verbatim:

> Note: The Tomorrow Open Source Technology License 1.0 differs from the
> original Apache License 2.0 in the following manner. Section 6 ("Trademarks")
> is different.

Its title is `TOMORROW OPEN SOURCE TECHNOLOGY LICENSE 1.0`. Each package
installs the complete upstream licence verbatim under `share/licenses/`.
The packaging files in this repository are MIT; that designation
does not replace the upstream licence. The pinned [licence text](https://github.com/jensjebens/OpenUSD/blob/1f6d6d31f1cbeed452b4e1c312bf974d0519d71d/LICENSE.txt)
is the authority for the upstream files.

## Deviations

- Validators require their own branch pin because the schema branch does
  not contain the validator package.
- The shared v0.3.10 structure lint recognizes semantic repositories, but
  has no `kit` kind, platform README headings or non-family source URL
  contract. The gate uses S01, S04, S25 and S26 plus explicit kit checks.
  `KitFlakeS05` enforces matching release-tag family URLs, recorded revisions,
  version literals matching library.json and a non-recursive builder input.
  It preserves the external fork URLs that shared S05 assumes belong to the
  family organization; it does not claim an unmodified S01–S29 pass.
- Native Python bindings use the development OpenUSD Python ABI. The
  ordinary usd-core wheel is used only for plugin-free composition.
- The shared builder's canonical resources are `lib/usdSolid/resources`.
  The requested `lib/usd/usdSolid/resources` path provides a forwarding
  descriptor and schema links. Both discovery paths are tested in fresh
  processes. The library remains `lib/libusdSolid.dylib` on Darwin.
- The validator pin contains 20 rules, including GeomSubsets, rather than
  the earlier count of 19.
- Upstream API declarations use `apiSchemaCanOnlyApplyTo =
  ["UsdSolidBrepArray"]`. In the pinned development runtime, `CanApply`
  raises an unknown-base-type error: applicability lookup expects the
  schema identifier `BrepArray`. Direct `Apply` and attribute authoring
  pass the upstream tests. This packaging preserves the class declarations;
  an upstream applicability fix remains outstanding.
- The v0.1.0 `nix flake check` attempt reached the acceptance gate and
  caught a bookkeeping error: the builder's annotated tag object had been
  recorded as its source revision. `dependencies.json` now records the
  peeled commit. Verification after this correction builds the acceptance
  derivation directly; the full flake command is not repeated.

## Fixture availability

The schema and validator pins include Python and C++ tests respectively.
Neither contains the separate five P2 example stages or the 66
`Test_BA_*.usda` producer fixtures. Their advertised counts are not a
verification result for these source trees.

The additional fixture input pins `feature/hdocct-tessellator` at
`d618f8ac62cefa02f6765d8e3784ea503195ce86`. Only the
`pxr/imaging/plugin/hdOcct/testenv/testUsdSolidTessellation/fixtures`
tree and `testenv/testCubeBrep.usda` are installed; no renderer is built.
The measured corpus contains **40 stages and 50 BrepArray prims**:
35 stages have no errors, five stages have 28 errors in total, and three
stages have five warnings in total. Native registry results and
`usdchecker --includeKeywords UsdSolidValidators` agree for every stage.

| Stage with errors | Errors | BA codes |
|---|---:|---|
| testCone.usda | 2 | BA.763 |
| testCubeBrep.usda | 6 | BA.005, BA.070, BA.085 |
| testFilletedCube.usda | 8 | BA.763 |
| testFilletedCubeWithHole.usda | 8 | BA.763 |
| testSphere.usda | 4 | BA.763 |

These are upstream fixture/validator disagreements at the recorded pins;
they are not fixed or suppressed here. The committed
[finding inventory](../testenv/expected/fixtures.json) preserves the complete
counts and identifiers. Its passing regression check establishes repeatable
findings, not validity of all 40 stages. The separate 66-fixture producer
acceptance and five P2 examples remain **not proven**.

Two independent mutations of the error-free producer cube verify rejection
of a negative intersection tolerance (`BA.010`) and an empty per-Brep extent
array (`BA.020`) through both the registry and the CLI. The unchanged
upstream suite contributes 17 Python tests and one native CTest executable.

## Reproducibility

`dependencies.json` records the hub, builder and three source revisions.
The family inputs use public GitHub names with the local override helper.
Deployment lockfiles are ignored because they contain private service
addresses. Direct upstream inputs are full revision pins; the hub pins its
nixpkgs and OpenUSD revisions. Private overrides live in the external `AECO_NIX_REGISTRY` JSON.

The source NAR hashes measured at fetch time are:

| Input | SHA-256 SRI |
|---|---|
| upstream | `sha256-tjYH1nNsZu3l0oFuOkNKRv7/zuuHj+BvXTtxziRykk0=` |
| upstream-validators | `sha256-3n3BGozaeN62VSTiy+meSIz79Oa187u3xT+r/xs4k/k=` |
| upstream-fixtures | `sha256-GiYRRrwmeORlNKMsQeo3960Mcrc0uCT1IY6BFtAd4TM=` |
