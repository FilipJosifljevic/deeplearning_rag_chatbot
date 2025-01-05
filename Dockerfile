FROM python:3.10-slim

WORKDIR /workspace

ENV OPENBLAS_NUM_THREADS=1
RUN mkdir -p /workspace/.cache/huggingface

COPY requirements.txt /workspace/requirements.txt

RUN pip3 config set global.index-url https://pypi.org/simple
RUN pip3 install --no-cache-dir --no-use-pep517 --proxy=http://ftn.proxy:8080 -r /workspace/requirements.txt --progress-bar off

ENV HTTP_PROXY=http://ftn.proxy:8080
ENV HTTPS_PROXY=http://ftn.proxy:8080
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface
