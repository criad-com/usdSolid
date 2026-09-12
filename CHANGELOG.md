# Changelog

## 0.1.5

- public re-pin: aeco-toolchain v0.4.0; usdaeco-toolchain v0.3.10.
- Import the native builders from the non-recursive toolchain source input;
  remove the obsolete recursive core override. Requirement ranges are unchanged.
- Record checked forge and public release revisions, accepting either exact
  commit for build provenance because public releases have independent history.
- Enforce release-tag family refs and flake version agreement in the kit pin
  gate, retaining the external OpenUSD fork URLs; add shared S04 pin validation.
- Verify 16 source tests and four shared structure rules. Native rebuild and
  cache publication remain blocked by uncached build dependencies; retain
  the v0.1.4 receipt unchanged and record the single offline flake attempt.

## 0.1.4

- Re-pin usdaeco-toolchain to v0.3.9, which fixes the Nix package version used by `pythonMetadataCheckPhase`; all other dependency pins are unchanged.
- Update the recorded toolchain revision and mark the cache receipt pending native rebuild and regeneration.
- Verify source checks only; native acceptance remains pending and `BLOCKED.md` is retained.

## 0.1.3

- public names → github.com/criad-com.

## 0.1.2

- License the packaging under MIT with SPDX headers on repository-owned sources.
- Retain the upstream Tomorrow Open Source Technology License 1.0 verbatim in each package.
- Bump packaging metadata; upstream pins, schema and native runtime behavior are unchanged.

## 0.1.1

- Re-pin to train aeco-0.7.0: usdaeco-toolchain v0.3.5; other kit pins unchanged.
- Read deployment overrides from the external registry required by the current term sweep.
- Prepare verified cache receipt generation; native rebuild and publication are blocked by missing build dependencies.

## 0.1.0

- Pin the upstream UsdSolid schema and native validator branches.
- Generate C++ and Python bindings through the shared native builder.
- Preserve upstream documentation, tests and licence at build time.
- Package 20 native validators and the separate 40-stage fixture corpus.
- Verify both resource layouts, plugin-free composition and seeded BA codes.
- Record 35 error-free stages and five stages with upstream validation errors.
