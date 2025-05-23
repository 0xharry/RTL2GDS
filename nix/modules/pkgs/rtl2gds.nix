{
  lib,
  bash,
  ieda,
  yosys,
  klayout,
  buildPythonPackage,
  python,
  setuptools,
  orjson,
  hatchling,
  requests,
  pyyaml,
  wheel,
  ipython,
}:
buildPythonPackage {
  pname = "rtl2gds";
  version = "0.0.1";
  pyproject = true;

  src =
    with lib.fileset;
    toSource {
      root = ./../../..;
      fileset = unions [
        ./../../../src
        ./../../../pyproject.toml
        ./../../../tests
        ./../../../tools
        ./../../../foundry
        ./../../../design_zoo
      ];
    };

  propagatedBuildInputs =
    [
      python
      pyyaml
      orjson
      klayout
      hatchling
      requests
      ipython
    ]
    ++ [
      ieda
      yosys
    ];

  nativeBuildInputs = [
    setuptools
    wheel
  ];

  makeWrapperArgs = [
    "--set PATH ${
      lib.makeBinPath [
        bash
        yosys
        ieda
      ]
    }"
    "--set LD_LIBRARY_PATH ${
      lib.makeLibraryPath [
        pyyaml
        orjson
        klayout
        ipython
      ]
    }"
  ];

  postInstall = ''
    mkdir -p $out/lib/${python.libPrefix}/tools/
    mkdir -p $out/lib/${python.libPrefix}/foundry/

    cp -r $src/tools/* $out/lib/${python.libPrefix}/tools/
    cp -r $src/foundry/* $out/lib/${python.libPrefix}/foundry/
  '';

  doCheck = false;

  meta = {
    description = "A tool to compile your RTL files into GDSII layouts.";
    homepage = "https://github.com/0xharry/RTL2GDS";
  };
}
