# syntax=docker/dockerfile:1
ARG BASE_IMAGE=ubuntu:20.04
FROM ${BASE_IMAGE}
LABEL maintainer="harry0789@qq.com"

ARG R2G_REPO=.
ARG R2G_WORKSPACE=/opt/rtl2gds
ARG BINARY_PATH="${R2G_WORKSPACE}/bin"

ENV PATH="${BINARY_PATH}/yosys/bin:${BINARY_PATH}/iEDA:$PATH"
ENV LD_LIBRARY_PATH="${BINARY_PATH}/lib"
ENV PYTHONPATH="${R2G_WORKSPACE}/src"

# syntax=docker/dockerfile:1.5-labs
# (docker build) --ssh default=$HOME/.ssh/id_rsa
ADD ${R2G_REPO} ${R2G_WORKSPACE}

RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install pyyaml orjson && \
    apt-get autoremove -y && apt-get clean -y

WORKDIR ${R2G_WORKSPACE}

CMD ["/usr/bin/env", "python3", "-m", "rtl2gds", "-h"]
