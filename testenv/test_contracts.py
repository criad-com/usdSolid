# SPDX-License-Identifier: MIT
import json
import pytest

from check_support import ROOT, check_pins, check_built_revisions
from prepare_schema import prepare
from prepare_validators import prepare as prepare_validator

VERSION = json.loads((ROOT / "library.json").read_text())["version"]


@pytest.fixture
def schema(tmp_path):
    path = tmp_path / "schema.usda"
    path.write_text('''#usda 1.0
over "GLOBAL" (
    customData = {
        string libraryName = "prelimUsdSolid"
        string libraryPath = "./"
    }
) {}
#************************************************************************************
class BrepArray "BrepArray" { double test:property = 1 }
''')
    return path


def test_build_metadata_preserves_schema_body(schema):
    before = schema.read_text().split('#*****', 1)[1]
    prepare(schema, "usdSolid")
    text = schema.read_text()
    assert text.split('#*****', 1)[1] == before
    assert 'libraryName = "usdSolid"' in text
    assert 'libraryPath = "pxr/usd/usdSolid"' in text
    assert 'useLiteralIdentifier = true' in text
    assert 'skipCodeGeneration = false' in text


@pytest.mark.parametrize("field", ["libraryName", "libraryPath"])
def test_missing_upstream_metadata_fails(schema, field):
    schema.write_text(schema.read_text().replace(field, "unknownField"))
    with pytest.raises(ValueError, match=field):
        prepare(schema, "usdSolid")


def test_dependency_pins_match_sources():
    assert check_pins(json.loads((ROOT / "dependencies.json").read_text()),
                      (ROOT / "flake.nix").read_text(), VERSION)


@pytest.mark.parametrize("mutation", ["revision", "missing", "follows"])
def test_pin_drift_fails(mutation):
    pins = json.loads((ROOT / "dependencies.json").read_text())
    flake = (ROOT / "flake.nix").read_text()
    if mutation == "revision":
        pins["repos"]["upstream"]["ref"] = "0" * 40
    elif mutation == "missing":
        del pins["repos"]["upstream-validators"]
    else:
        flake = flake.replace('nixpkgs.follows', 'nixpkgs.other')
    with pytest.raises(AssertionError):
        check_pins(pins, flake, VERSION)


@pytest.mark.parametrize("name", ["aeco-toolchain", "usdaeco-toolchain"])
def test_matching_family_hash_pins_fail(name):
    pins = json.loads((ROOT / "dependencies.json").read_text())
    flake = (ROOT / "flake.nix").read_text()
    tag = pins["repos"][name]["ref"]
    revision = pins["repos"][name]["revision"]
    pins["repos"][name]["ref"] = revision
    flake = flake.replace(f'{name}?ref={tag}', f'{name}?ref={revision}')
    with pytest.raises(AssertionError, match="release tags"):
        check_pins(pins, flake, VERSION)


@pytest.mark.parametrize("mutation", ["version", "tag-as-revision", "recursive-toolchain"])
def test_kit_flake_contract_rejects_drift(mutation):
    pins = json.loads((ROOT / "dependencies.json").read_text())
    flake = (ROOT / "flake.nix").read_text()
    if mutation == "version":
        flake += '\nversion = "0.0.0";\n'
    elif mutation == "tag-as-revision":
        flake = flake.replace('aeco-toolchain?ref=', 'aeco-toolchain?rev=')
    else:
        flake = flake.replace('usdaeco-toolchain.flake = false;', '')
    with pytest.raises(AssertionError):
        check_pins(pins, flake, VERSION)


@pytest.mark.parametrize("public", [False, True])
def test_checked_release_revisions_are_accepted(public):
    pins = json.loads((ROOT / "dependencies.json").read_text())
    revisions = {name: pin.get("publicRevision" if public else "revision", pin["ref"])
                 for name, pin in pins["repos"].items()}
    assert check_built_revisions({"revisions": revisions}, pins)


def test_unchecked_build_revision_fails():
    pins = json.loads((ROOT / "dependencies.json").read_text())
    revisions = {name: pin.get("revision", pin["ref"]) for name, pin in pins["repos"].items()}
    revisions["aeco-toolchain"] = "0" * 40
    with pytest.raises(AssertionError, match="Build revision differs"):
        check_built_revisions({"revisions": revisions}, pins)


def test_descriptor_adaptation_preserves_rules(tmp_path):
    rules = {f"Rule{i}": {"doc": "A rule", "schemaTypes": ["UsdSolidBrepArray"]} for i in range(20)}
    rules["keywords"] = ["UsdSolidValidators"]
    source = tmp_path / "input.json"
    target = tmp_path / "plugInfo.json.in"
    source.write_text(json.dumps({"Plugins": [{"Name": "usdSolidValidators", "Type": "library",
                                               "Info": {"Validators": rules}}]}))
    prepare_validator(source, target)
    output = json.loads(target.read_text().replace("@AECO_METADATA@", "{}"))["Plugins"][0]
    assert output["Info"]["Validators"] == rules
    assert output["LibraryPath"].startswith("../@CMAKE_SHARED_LIBRARY_PREFIX@")
    assert output["Root"] == ".."
