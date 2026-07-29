FROM python:3.14.2-slim-bookworm

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    libmariadb-dev \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev \
    pkg-config \
    nano \
    iputils-ping \
    net-tools \
    iproute2

WORKDIR /build
COPY requirements.txt .
RUN pip install -r requirements.txt