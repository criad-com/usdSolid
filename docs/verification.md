# Verification record

## v0.1.6 documentation patch

The release docs state the measured acceptance and publication results
directly. Release metadata is 0.1.6 in both manifests, both CMake projects,
pyproject.toml and the gate; dependency pins and requirement ranges are unchanged.

| Acceptance | Result |
|---|---|
| Source pytest | 16 passed |
| Shared structure lint | 4 checks, 0 failed: S01, S04, S25, S26 from v0.3.10 |
| Documentation reference sweep | 0 references to the removed branch-only status file in tracked files |
| Whitespace | `git diff --check` clean |
| Native rebuild / `nix flake check` | Not run for this documentation patch; v0.1.6 native acceptance is not proven |
| Cache receipt | Published v0.1.5 receipt retained byte-for-byte; 78 closure paths, 3 verified artifacts |

### Deviations

Native v0.1.6 acceptance and a regenerated receipt remain for the reviewer.
The existing runtime was checked once against the unmodified v0.1.5 source
before the version bump, with the results below.

## v0.1.5 publication

The committed [cache receipt](cache-receipt.json) records a successful
v0.1.5 publication: push exit code 0, 78 closure paths and three verified
artifacts (schema, validators and runtime). The recorded input revisions
match `dependencies.json`.

The published runtime passes **29 checks, 0 failed, 0 not run**, including
13 classes, 20 validators, 17 upstream Python tests and the native validator
executable. Plugin-free composition passes, and the two seeded BA codes
are independently rejected. All 40 fixture stages / 50 Breps match the
expected findings: 35 error-free stages, five with errors, 28 errors and
five warnings; the CLI agrees for all 40 stages.

These release results supersede the initial attempt below, which used
stale v0.1.4 artifacts. They do not establish v0.1.6 native acceptance.

## v0.1.5 initial public re-pin checks

This section records the source checks and unsuccessful offline attempt
before the v0.1.5 publication above.

Both family release tags were checked directly on the forge and public
GitHub repositories. Annotated forge tags were peeled to their commits.
`revision` records that checked forge commit; `publicRevision` records the
independent public release commit. The build gate accepts those two exact
commits and rejects arbitrary replacements.

| Input | Tag | Checked revision | Public revision |
|---|---|---|---|
| aeco-toolchain | v0.4.0 | `71c86d54aa1e4be180a301a089d9a40e727758cb` | `afbea7ce2b012e55af54047311fad37339eb56df` |
| usdaeco-toolchain | v0.3.10 | `59d3da5ff5114089b54efaaae38efdd7fe1b8e73` | `6328e1b5e63f89ea87984ad240b5c3ca37974795` |

The builder is now a source input (`flake = false`). Importing its outputs
with the existing Nix inputs reuses its native builders without fetching its
test-only core dependency. The obsolete recursive core override is removed.

| Acceptance | Result |
|---|---|
| Release metadata | 0.1.5 in both manifests, both CMake projects, pyproject.toml and the gate; no separately versioned Python source package |
| Family pins | 2/2 published tags verified; no family commit-hash URL refs |
| External source pins | 3/3 unchanged |
| Requirement ranges | Unchanged; validator requirement remains `>=0.1,<0.2` |
| Source pytest | 16 passed |
| Shared structure lint | 4 checks, 0 failed: S01, S04, S25, S26 from v0.3.10 |
| KitFlakeS05 | Pass; rejects matching family hash pins, stale flake version literals, tag-as-revision URLs and recursive builder inputs |
| Public-name / whitespace checks | 0 obsolete public-org refs; `git diff --check` clean |
| Build preflight, store only | 1,197 planned derivations; no build started |
| Build preflight, permitted cache | 1,114 planned derivations; bootstrap/build dependencies remain unavailable; no build started |
| `nix flake check` | Exactly 1 attempt, exit 1; offline, no lockfile write, local checkout overrides; native outputs and acceptance derivation evaluate |
| `check.py`, existing v0.1.4 runtime | 29 checks, 3 failed, 0 not run; BuiltRevisions and both plugin metadata checks correctly reject stale artifacts |
| Runtime regression, existing v0.1.4 runtime | Other 26 checks pass: 13 classes, 20 validators, 17 upstream Python tests and native validator executable |
| Fixture regression, existing v0.1.4 runtime | 40 stages / 50 Breps; 35 error-free, 5 with errors; 28 errors and 5 warnings; CLI agrees for all 40 |
| Plugin-free / seeded defects, existing v0.1.4 runtime | Composition passes; BA.010 and BA.020 independently rejected |
| Existing committed fixture data | Vanilla stage and expected findings byte-identical to v0.1.4 |
| Native rebuild / regenerated schema comparison | Not proven for v0.1.5 |
| Cache receipt | v0.1.4 receipt retained byte-for-byte; 78 closure paths, 3 verified artifact hashes are historical evidence |
| Published example layers / vanilla renders | Not applicable to this native kit; no committed example result tree |

The offline command was the README's local checkout override pattern, using
the exact checked revisions above and additionally `--max-jobs 0 --option
substituters '' --option extra-substituters ''`. Disabling local builds
prevented uncached fetch derivations from contacting additional hosts.
Nix stopped at `h9n1zm5zn2j9i0fjwldh7jgbp6svb3br-source.drv`, reporting
that no suitable builder was available. This is a missing dependency with
builds disabled, not evidence of an architecture mismatch. No second
flake-check attempt was made.

### Deviations

- The initial environment could not supply a native rebuild, green gate,
  cache publication or regenerated receipt. The later v0.1.5 publication
  records 78 closure paths and three verified artifacts, and the published
  runtime now passes all 29 gate checks as recorded above.
- A provenance-only native result diff is **not proven**. All three upstream
  pins and the committed fixture data are unchanged. The toolchain's v0.3.10
  changelog states that the OpenUSD output is unchanged; its native CMake/Nix
  builders and plugin-set helper have no source diff from v0.3.9. These are
  source-level observations, not a replacement for rebuilding and comparing
  generated schema and fixture bytes.
- Shared S05 assumes family-owned URLs for every input, including external
  OpenUSD sources. The explicit kit equivalent retains the existing fork
  URLs and enforces the new tag/version rules. S02/S03 remain explicit kit
  checks because shared metadata and README rules have no kit form.
- Public tags were independently verified. Complete public flake resolution
  and online acceptance remain for review; the one flake attempt used local
  sources. No Linux build was attempted.

## Historical v0.1.4 publication

The v0.1.4 publication recorded 78 closure paths and three artifact hashes.
Its runtime was used for the initial re-pin regression measurements above.
The committed receipt now records v0.1.5 publication instead.

The existing limitations remain: five P2 examples and the separate
66-defect producer corpus are absent from the pinned sources, and upstream
`CanApply` declarations have an applicability-name issue. See
[the measured source limitations](upstream.md#fixture-availability).
