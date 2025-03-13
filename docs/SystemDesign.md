# 系统设计文档

`RTL2GDS`是一款将您的RTL设计转化为可制造版图的工具。本文档对`RTL2GDS`从背景、需求、设计思路到实施路线图进行描述。

## 1 背景

芯片从设计到制造，越走向下游，资产越重，商业EDA公司含量越高。开源工具想要在市场中获得一席之地需要整合现有生态资源，并充分发挥社区力量。在RTL到GDS流程上，市面上已经存在如 `OpenLane`、`SiliconCompiler` 等优秀开源工具，由商业公司维护，并成功进行若干次流片（参考[开源EDA工具链项目动态表]）。作为后发追赶者，我们整合CC社区芯片设计流片经验、“一生一芯”教学经验和EDA工具研发经验，本着促进CC社区开源芯片项目发展和 Learning-by-doing 的理念，基于开源iEDA，构建支持PPA评估和版图生成的EDA工具 `RTL2GDS` 和全流程设计模板库 `Design Zoo`。期望和来自芯片、EDA等社区的爱好者和开发者一起构建与迭代开源芯片生态。

## 2 需求

## 2.1 目标用户

（欢迎选择您的角色，欢迎pr补充）

- ysyx学员
- 云平台

### 2.2 功能需求

| 需求编号 | 需求描述 | 输入 | 输出 |
| --- | --- | --- | --- |
| 1 | RTL到GDS设计 | 配置文件, RTL | 评估报告, GDS, 版图俯视图 |
| 2 | 单步执行-综合 | 配置文件, RTL | 评估报告, 网表, 连接关系图 |
| 3 | 单步执行-floorplan | 配置文件, 网表, Macro | 评估报告, def, 版图俯视图 |
| 4 | 单步执行-placement/cts/opt/routing | 配置文件, def | 评估报告, def, 版图俯视图 |
| 5 | 单步执行-物理验证 | 配置文件, def | 评估报告 |

Notes：

- 配置文件为yaml格式，包含RTL基础信息（Top名）、结果/报告文件路径、设计约束（时序/面积/利用率）
<!-- - 输出通常还包含当前阶段的版图俯视图，为图片格式。 -->

## 3 模块设计

### 3.1 Chip-芯片设计信息

包含关键文件路径、设计约束、运行时上下文、metrics等

RTL2GDS功能核心，由Flow进行修改

### 3.2 Flow-芯片设计流程

基于Step构建，使用Chip进行上下文信息传递

- RTL2GDS

RTL2GDS全流程，对应需求1

linear sequential flow

- CloudFlow

由 HTTP RESTful api 请求调用，启动容器，通过容器入口命令传递参数。在 `cloud_main.py` 构造 `CloudFlow` 并运行。关键参数如下：

| IO | Arguements | Avaliable Values | Source |
|---|---|---|---|
| Input | config path | "/path/to/config.yaml" | API request body |
| Input | step | "rtl2gds", "route" | API request body |
| Output | container info | container_id | docker python api |


### 3.3 Step-执行工具封装

约定执行步骤的标准输入和输出，进行信息验证和工具功能执行
封装了包含iEDA、yosys和klayout在内的开源EDA工具
