# tag: rtl2gds:magic
ARG BASE_IMG=rtl2gds:v0630
ARG R2G_FINAL_IMG=rtl2gds:v0630

FROM $BASE_IMG AS base

FROM $R2G_FINAL_IMG

ADD demo/magicsrc /opt/magic

RUN apt-get install -y --no-install-recommends \
    m4 libx11-dev tcl-dev tk-dev libcairo2-dev libncurses-dev zlib1g-dev && \
    cd /opt/magic && ./configure && make -j 32 && make install -j 32

COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/lib /usr/local/lib

ARG R2G_WORKSPACE=/opt/rtl2gds
WORKDIR ${R2G_WORKSPACE}

CMD ["/usr/bin/env", "python3", "-m", "rtl2gds", "-h"]
