FROM python:3.8

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt install -y curl \
    && curl -sL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt install -y nodejs \
    && apt-get install -y libglu1 \
    && pip install psycopg2 \
    && pip install psycopg2-binary

RUN pip install --upgrade pip \
  && pip install pipenv

COPY ./Pipfile /usr/src/app/Pipfile

RUN pipenv install --skip-lock --system --dev

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
