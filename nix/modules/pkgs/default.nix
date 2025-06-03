{
  pkgs,
  inputs',
  ...
}:
let
  iedaUnstable = inputs'.ieda-infra.packages.ieda;
in
{
  packages = {
    default = pkgs.python3Packages.callPackage ./rtl2gds.nix { inherit iedaUnstable; };
    ieda = iedaUnstable;
  };

}
