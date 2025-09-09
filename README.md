# RTL to GDSII Flow

<div align="left">

![GitHub workflows](https://img.shields.io/github/actions/workflow/status/0xharry/RTL2GDS/test.yml)
![GitHub issues](https://img.shields.io/github/issues/0xharry/RTL2GDS)
![GitHub pull requests](https://img.shields.io/github/issues-pr/0xharry/RTL2GDS)

</div>

A tool to compile your RTL files into GDSII layouts.

## Table of Contents

- [RTL to GDSII Flow](#rtl-to-gdsii-flow)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Usage](#usage)
    - [0. Setup Runtime Environment](#0-setup-runtime-environment)
    - [1. Prepare File Inputs](#1-prepare-file-inputs)
    - [2. Run RTL2GDS flow](#2-run-rtl2gds-flow)
    - [3. Run Single Step Flow](#3-run-single-step-flow)
  - [Contributing](#contributing)

## Overview

`rtl2gds` is an open-source tool designed to convert RTL (verilog) designs into GDSII layouts. It supports various RTL designs and includes examples to help you get started quickly.

## Usage

### 0. Setup Runtime Environment

`rtl2gds` depends on [iEDA](https://gitee.com/oscc-project/iEDA), [yosys](https://github.com/YosysHQ/yosys) and [magic-vlsi](http://opencircuitdesign.com/magic/).

A prebuilt yosys binary is presented at `/rtl2gds/bin/yosys`, but we recommend you to install yosys from [oss-cad-suite-build](https://github.com/YosysHQ/oss-cad-suite-build/releases/),
which is a prebuilt binary package for yosys and other EDA tools (We will use the yosys-slang plugin in the project).

Build iEDA from source code, [here](https://gitee.com/oscc-project/iEDA/blob/master/README.md#method-2--install-dependencies-and-compile) is how you do it:

```shell
# git clone https://atomgit.com/harrywh/rtl2gds.git && cd rtl2gds
# works for ubuntu 20.04 and 22.04
git clone --recursive https://gitee.com/oscc-project/iEDA.git iEDA && cd iEDA
sudo bash build.sh -i apt
bash build.sh
# succeed if prints "Hello iEDA!"
./bin/iEDA -script scripts/hello.tcl
mv ./bin/iEDA ../bin/iEDA/iEDA
export RTL2GDS_USE_PROJ_BIN_LIB=1
# install klayout, yosys and magic, see Dockerfile
```

### 1. Prepare File Inputs

Prepare your RTL design (Verilog files), and configuration (yaml file).

`design_zoo` includes several example designs to help you get started:

- `gcd`: A simple GCD calculator, single Verilog file
- `picorv32a`: A RISC-V CPU core, single Verilog file
- `aes`: An AES encryption module, multiple Verilog files

### 2. Run RTL2GDS flow

Using the [official RTL2GDS image](docker.cnb.cool/ecoslab/rtl2gds)

To compile your design, use the following commands:

```shell
$ cd RTL2GDS # make sure you are in the root directory of RTL2GDS
$ docker run --rm -it -v $(pwd):/opt/rtl2gds docker.cnb.cool/ecoslab/rtl2gds:latest bash
# Enter the design directory, e.g., cd /opt/rtl2gds/design_zoo/gcd
$ python3 -m rtl2gds -c <your-design-config>.yaml
```

### 3. Run Single Step Flow

The single step flow allows you to run individual steps of the RTL2GDS flow separately, which is useful for debugging, testing, or running specific stages of the design flow.

**Available Steps:**
- `synthesis` - Synthesize RTL to netlist
- `floorplan` - Create floorplan
- `netlist_opt` - Optimize netlist
- `placement` - Place cells
- `cts` - Clock tree synthesis
- `legalization` - Legalize placement
- `routing` - Route connections

**Usage:**

```shell
$ cd RTL2GDS # make sure you are in the root directory of RTL2GDS
$ docker run --rm -it -v $(pwd):/opt/rtl2gds docker.cnb.cool/ecoslab/rtl2gds:latest bash
# Enter the design directory, e.g., cd /opt/rtl2gds/design_zoo/gcd
$ python3 -m rtl2gds.flow.single_step_main -c <your-design-config>.yaml --step <step-name>
```

**Additional Options:**
- `--log_level` - Set log level (DEBUG, INFO, WARNING, ERROR)
- `--take_snapshot` - Take snapshot of current step
- `--cloud_outputs` - Generate cloud outputs (layout json)
- `--result_dir` - Custom result directory path
- `--input_def` - Custom input DEF file path for routing steps

**Example:**

```shell
# Run only the synthesis step
$ python3 -m rtl2gds.flow.single_step_main -c gcd.yaml --step synthesis

# Run synthesis with custom result directory
$ python3 -m rtl2gds.flow.single_step_main -c gcd.yaml --step synthesis --result_dir my_results

# Run routing with custom input DEF file
$ python3 -m rtl2gds.flow.single_step_main -c gcd.yaml --step routing --input_def custom_input.def
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
