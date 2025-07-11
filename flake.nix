{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
    ieda-infra.url = "github:Emin017/ieda-infra";
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      parts,
      treefmt-nix,
      ieda-infra,
      ...
    }:
    parts.lib.mkFlake { inherit inputs; } {
      imports = [
        treefmt-nix.flakeModule
      ];
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      perSystem =
        {
          inputs',
          self',
          pkgs,
          system,
          ...
        }:
        {
          devShells = {
            default = pkgs.mkShell {
              nativeBuildInputs = [
                pkgs.python3
                pkgs.python3Packages.pip
                pkgs.python3Packages.virtualenv
                pkgs.git
                pkgs.black
              ];
              shellHook = ''
                export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
              '';
            };
            ieda = pkgs.mkShell {
              inputsFrom = [
                inputs'.ieda-infra.packages.iedaUnstable
              ];
              nativeBuildInputs = [
                pkgs.black
              ];
            };
          };
          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              nixfmt.enable = true;
              nixfmt.package = pkgs.nixfmt-rfc-style;
              black.enable = true;
            };
            flakeCheck = true;
          };
        };
    };
}
