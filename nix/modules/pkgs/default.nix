{ pkgs, ... }:
{
  packages.default = pkgs.python3Packages.callPackage ./rtl2gds.nix { };
}
