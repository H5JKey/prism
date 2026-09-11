FROM archlinux:latest

ARG BUILD_MODE
ARG BUILD_TESTS=OFF

WORKDIR /renderer

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    gcc \
    make \
    cmake \
    git \
    mesa \
    mesa-utils \
    python-jinja \
    librdkafka \
    openimagedenoise \
    aws-sdk-cpp \
    boost \
    boost-libs \
    libglvnd \
    libx11 \
    libxrandr \
    libxinerama \
    libxcursor \
    libxi \
&& pacman -Scc --noconfirm

COPY renderer/ .
RUN mkdir build && cd build && cmake .. -DBUILD_MODE=${BUILD_MODE} -DBUILD_TESTS=${BUILD_TESTS}
RUN cd build && make -j$(nproc)

ENV PATH="/renderer/build:${PATH}"