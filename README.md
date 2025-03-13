# RTL to GDSII Flow

A tool to compile your RTL files into GDSII layouts.

## Table of Contents

- [RTL to GDSII Flow](#rtl-to-gdsii-flow)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Usage](#usage)
    - [0. Setup Runtime Environment](#0-setup-runtime-environment)
    - [1. Prepare File Inputs](#1-prepare-file-inputs)
    - [2. Run RTL2GDS flow](#2-run-rtl2gds-flow)
  - [Contributing](#contributing)

## Overview

`rtl2gds` is an open-source tool designed to convert RTL (verilog) designs into GDSII layouts. It supports various RTL designs and includes examples to help you get started quickly.

## Usage

### 0. Setup Runtime Environment

`rtl2gds` depends on [iEDA](https://gitee.com/oscc-project/iEDA) and [yosys](https://github.com/YosysHQ/yosys). A prebuilt yosys binary is presented at `/rtl2gds/bin/yosys`

Build iEDA from source code, [here](https://gitee.com/oscc-project/iEDA/blob/master/README.md#method-2--install-dependencies-and-compile) is how you do it:

```shell
# git clone https://atomgit.com/harrywh/rtl2gds.git && cd rtl2gds
# only works for ubuntu 20.04
git clone --recursive https://gitee.com/oscc-project/iEDA.git iEDA && cd iEDA
sudo bash build.sh -i apt
bash build.sh
# succeed if prints "Hello iEDA!"
./bin/iEDA -script scripts/hello.tcl
mv ./bin/iEDA ../bin/iEDA/iEDA
```

### 1. Prepare File Inputs

Prepare your RTL design (Verilog files), and configuration (yaml file).

`design_zoo` includes several example designs to help you get started:

- `gcd`: A simple GCD calculator, single Verilog file
- `picorv32a`: A RISC-V CPU core, single Verilog file
- `aes`: An AES encryption module, multiple Verilog files

### 2. Run RTL2GDS flow

`rtl2gds` has been tested on the following Docker images: `ubuntu:20.04`, `ubuntu:22.04`, `debian:11`, and `debian:12`.

To compile your design, use the following commands:

```shell
$ cd RTL2GDS # make sure you are in the root directory of RTL2GDS
$ docker run --rm -it -v $(pwd):/rtl2gds -e PYTHONPATH="/rtl2gds/src" ubuntu:22.04 bash
# After entering the container, you can run the following commands
$ cd /rtl2gds && apt update && apt install -y python3 python3-pip libcurl4-openssl-dev libexpat1-dev libpng-dev && pip3 install pyyaml orjson klayout
# Then enter the design directory, e.g., /rtl2gds/design_zoo/gcd
$ python3 -m rtl2gds -c <your-design-config>.yaml
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
