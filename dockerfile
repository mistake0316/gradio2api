FROM python:3.11

RUN pip install -U gradio
RUN pip install -U gradio-client
RUN pip install -U "fastapi[standard]"
RUN pip install -U uvicorn

COPY src /src
WORKDIR /src

ENV PYTHONPATH=/src:$PYTHONPATH

CMD [ bash ]