{
  pkgs,
  inputs',
  self',
  ...
}:
{
  devShells = {
    default = pkgs.mkShell {
      nativeBuildInputs =
        with pkgs;
        [
          python3
          python3Packages.pip
          python3Packages.virtualenv
          git
          black
          isort
          uv
        ]
        ++ [ self'.packages.collectMetrics ];
      shellHook = ''
        export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
      '';
    };
    ieda = pkgs.mkShell {
      inputsFrom = [
        inputs'.ieda-infra.packages.iedaUnstable
      ];
      nativeBuildInputs = with pkgs; [
        black
      ];
    };
  };
}
