{ pkgs, ... }:
{
  treefmt = {
    projectRootFile = "flake.nix";
    programs = {
      nixfmt.enable = true;
      nixfmt.package = pkgs.nixfmt-rfc-style;
      black.enable = true;
    };
    flakeCheck = true;
  };
}
