ARG BASE_IMAGE=ubuntu:20.04
FROM ${BASE_IMAGE}
LABEL maintainer="harry0789@qq.com"

RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y python3-pip curl&& \
    pip3 install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple pyyaml requests fastapi uvicorn && \
    apt-get autoremove -y && apt-get clean -y

# syntax=docker/dockerfile:1.5-labs
# (docker build) --ssh default=$HOME/.ssh/id_rsa
ARG R2G_REPO=.
ARG R2G_WORKSPACE=/opt/r2gcloud
ADD ${R2G_REPO} ${R2G_WORKSPACE}

WORKDIR ${R2G_WORKSPACE}
