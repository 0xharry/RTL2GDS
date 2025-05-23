{ pkgs, ... }:
{
  devShells =
    let
      deps = with pkgs; [
        yosys
        ieda
        python312
        python312Packages.pyyaml
        python312Packages.orjson
        python312Packages.klayout
        python312Packages.pip
      ];
    in
    {
      default = pkgs.mkShell {
        buildInputs = deps;
        shellHook = ''
          export PYTHONPATH=`pwd`/src
        '';
      };
    };
}
