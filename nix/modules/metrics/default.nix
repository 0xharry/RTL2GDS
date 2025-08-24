{
  pkgs,
  ...
}:
{
  packages.collectMetrics = pkgs.stdenvNoCC.mkDerivation {
    name = "collectMetrics";

    nativeBuildInputs = with pkgs; [
      makeShellWrapper
    ];

    dontUnpack = true;

    installPhase = ''
      mkdir -p $out/bin
      cp ${./collect-metrics.sh} $out/bin/.collect-metrics-unwrapped
      chmod +x $out/bin/.collect-metrics-unwrapped
      makeShellWrapper $out/bin/.collect-metrics-unwrapped $out/bin/collect-metrics \
        --prefix PATH : "${pkgs.jq}/bin"
    '';
  };
}
