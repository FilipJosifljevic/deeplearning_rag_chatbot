FROM python:3.10-slim

WORKDIR /workspace

COPY requirements.txt /workspace/requirements.txt

RUN pip3 config set global.index-url https://pypi.org/simple
RUN pip3 install --no-cache-dir --no-use-pep517 -r /workspace/requirements.txt --progress-bar off

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api_rag:app", "--host", "0.0.0.0", "--port", "8000"]
