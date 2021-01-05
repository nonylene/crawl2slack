# vim: set ft=dockerfile :
FROM python:slim
WORKDIR /app

RUN pip3 install poetry

COPY ./poetry.lock ./pyproject.toml /app/
RUN poetry install --no-dev

ENV PYTHONUNBUFFERED=1

RUN poetry install

COPY LICENSE /app/
COPY DOCKER_NOTICE /app/
COPY main.py /app/

ENTRYPOINT ["poetry", "run", "python3", "main.py"]
