# SPDX-License-Identifier: MIT
{
  description = "Codeful UsdSolid schema and native validation plugins";
  inputs = {
    aeco-toolchain.url = "github:criad-com/aeco-toolchain?ref=v0.4.0";
    usdaeco-toolchain.url = "github:criad-com/usdaeco-toolchain?ref=v0.3.10";
    usdaeco-toolchain.flake = false;
    nixpkgs.follows = "aeco-toolchain/nixpkgs";
    upstream = {
      url = "github:jensjebens/OpenUSD?rev=1f6d6d31f1cbeed452b4e1c312bf974d0519d71d";
      flake = false;
    };
    upstream-validators = {
      url = "github:jensjebens/OpenUSD?rev=152c37a46c8cb71fbe1363772f1ccffe6e91c78b";
      flake = false;
    };
    upstream-fixtures = {
      url = "github:jensjebens/OpenUSD?rev=d618f8ac62cefa02f6765d8e3784ea503195ce86";
      flake = false;
    };
  };
  outputs = { self, nixpkgs, aeco-toolchain, usdaeco-toolchain, upstream, upstream-validators, upstream-fixtures }:
    let
      # Import only the builders from the source pin, without resolving its test inputs.
      builders = (import (usdaeco-toolchain + "/flake.nix")).outputs {
        self = usdaeco-toolchain;
        inherit nixpkgs aeco-toolchain;
        core = null; # Used only by the toolchain's own checks.
      };
      systems = [ "aarch64-darwin" "x86_64-linux" ];
      eachSystem = nixpkgs.lib.genAttrs systems;
      forSystem = system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          inherit (pkgs) lib;
          name = import ./nix/library-name.nix;
          kit = builders.lib.forSystem system;
          usd-dev = aeco-toolchain.packages.${system}.usd-dev;
          compatInstall = plugin: ''
            mkdir -p "$out/lib/usd/${plugin}/resources"
            printf '{"Includes":["../../../${plugin}/resources/"]}\n' \
              > "$out/lib/usd/${plugin}/resources/plugInfo.json"
          '';
          schemaSrc = lib.fileset.toSource {
            root = ./.;
            fileset = lib.fileset.unions [ ./library.json ./nix/schema
              ./tools/prepare_schema.py ./testenv/testRegistry.py ];
          };
          usdSolid = (builders.lib.buildCodefulSchema {
            inherit system name;
            src = schemaSrc;
          }).overrideAttrs (old: {
            postInstall = old.postInstall + compatInstall name + ''
              ln -s ../../../${name}/resources/generatedSchema.usda \
                "$out/lib/usd/${name}/resources/generatedSchema.usda"
              ln -s ../../../${name}/resources/${name}/schema.usda \
                "$out/lib/usd/${name}/resources/schema.usda"
            '';
            postUnpack = ''
              echo "== stage: pinned schema source"
              cp "$sourceRoot/nix/schema/CMakeLists.txt" "$sourceRoot/CMakeLists.txt"
              mkdir -p "$sourceRoot/${name}"
              for item in schema.usda module.cpp __init__.py userDoc examples testenv; do
                if test -e ${upstream}/pxr/usd/usdSolid/"$item"; then
                  cp -R ${upstream}/pxr/usd/usdSolid/"$item" "$sourceRoot/${name}/"
                fi
              done
              cp ${upstream}/LICENSE.txt "$sourceRoot/UPSTREAM-LICENSE.txt"
              chmod -R u+w "$sourceRoot"
              substituteInPlace "$sourceRoot/${name}/__init__.py" \
                --replace-fail 'from pxr import Tf' 'from pxr import Tf, UsdGeom'
              env -u PYTHONPATH ${kit.nativePython}/bin/python \
                "$sourceRoot/tools/prepare_schema.py" "$sourceRoot/${name}/schema.usda" ${name}
            '';
          });
          validatorSrc = lib.fileset.toSource {
            root = ./nix/validators;
            fileset = ./nix/validators;
          };
          usdSolidValidators = (builders.lib.buildNativePlugin {
            inherit system;
            name = "usdSolidValidators";
            src = validatorSrc;
            deps = [ usdSolid ];
            cmakeFlags = [ "-DUSDSOLID_PLUGIN_PATH=${usdSolid}/lib" ];
          }).overrideAttrs (old: {
            postUnpack = ''
              echo "== stage: pinned validator source"
              cp -R ${upstream-validators}/pxr/usdValidation/usdSolidValidators "$sourceRoot/"
              cp ${upstream-validators}/LICENSE.txt "$sourceRoot/UPSTREAM-LICENSE.txt"
              chmod -R u+w "$sourceRoot"
              env -u PYTHONPATH ${kit.nativePython}/bin/python ${./tools/prepare_validators.py} \
                "$sourceRoot/usdSolidValidators/plugInfo.json" "$sourceRoot/plugInfo.json.in"
            '';
            postInstall = old.postInstall + compatInstall "usdSolidValidators";
          });
          fixtures = pkgs.runCommand "usdSolid-upstream-fixtures" { } ''
            mkdir -p "$out"
            cp -R ${upstream-fixtures}/pxr/imaging/plugin/hdOcct/testenv/testUsdSolidTessellation/fixtures/. "$out/"
            cp ${upstream-fixtures}/pxr/imaging/plugin/hdOcct/testenv/testCubeBrep.usda "$out/"
            cp ${upstream-fixtures}/LICENSE.txt "$out/UPSTREAM-LICENSE.txt"
          '';
          schemaPython = pkgs.python3.pkgs.toPythonModule (pkgs.runCommand "usdSolid-python" { } ''
            mkdir -p "$out/${pkgs.python3.sitePackages}/pxr"
            ln -s ${usdSolid}/${pkgs.python3.sitePackages}/pxr/UsdSolid "$out/${pkgs.python3.sitePackages}/pxr/UsdSolid"
          '');
          pythonEnv = pkgs.python3.withPackages (ps: [ kit.usdPython schemaPython ps.pytest ps.packaging ]);
          pluginSet = kit.pluginSet { plugins = [ usdSolidValidators ]; };
          runtime = pkgs.runCommand "usdSolid-runtime" { } ''
            mkdir -p "$out"
            cat > "$out/paths.json" <<'JSON'
            ${builtins.toJSON {
              schema = "${usdSolid}";
              validators = "${usdSolidValidators}";
              python = "${pythonEnv}/bin/python";
              checker = "${usd-dev}/bin/usdchecker";
              plugins = "${pluginSet}";
              fixtures = "${fixtures}";
              toolchain = "${usdaeco-toolchain}";
              upstream = "${upstream}";
              upstreamValidators = "${upstream-validators}";
              revisions = {
                aeco-toolchain = aeco-toolchain.rev;
                usdaeco-toolchain = usdaeco-toolchain.rev;
                upstream = upstream.rev;
                upstream-validators = upstream-validators.rev;
                upstream-fixtures = upstream-fixtures.rev;
              };
            }}
            JSON
          '';
        in { inherit pkgs kit usd-dev usdSolid usdSolidValidators pythonEnv fixtures pluginSet runtime; };
    in {
      packages = eachSystem (system: let p = forSystem system; in {
        inherit (p) usdSolid usdSolidValidators pythonEnv fixtures pluginSet runtime;
        default = p.usdSolid;
      });
      checks = eachSystem (system: let p = forSystem system; in {
        schema = p.usdSolid;
        validators = p.usdSolidValidators;
        acceptance = p.pkgs.runCommand "usdSolid-acceptance" {
          nativeBuildInputs = [ p.pythonEnv ];
        } ''
          export USD_SOLID_RUNTIME=${p.runtime}
          export USDAECO_TOOLCHAIN_DIR=${usdaeco-toolchain}
          cp -R ${self} source
          chmod -R u+w source
          cd source
          env -u PYTHONPATH ${p.pythonEnv}/bin/python check.py
          echo "== stage: source pytest"
          env -u PYTHONPATH ${p.pythonEnv}/bin/python -m pytest -q
          touch "$out"
        '';
      });
      devShells = eachSystem (system: let p = forSystem system; in {
        default = p.pkgs.mkShell {
          packages = [ p.pythonEnv p.usd-dev p.usdSolid p.usdSolidValidators ];
          shellHook = ''
            unset PYTHONPATH
            export PXR_PLUGINPATH_NAME=${p.pluginSet}
            export USD_SOLID_RUNTIME=${p.runtime}
            export USDAECO_TOOLCHAIN_DIR=${usdaeco-toolchain}
          '';
        };
      });
    };
}
