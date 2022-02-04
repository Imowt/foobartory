FROM python:3.9.4-slim

COPY foobartory /src/foobartory
COPY Pipfile /src
COPY .env /src

WORKDIR /src

RUN pip install --upgrade pip

RUN pip install pipenv

RUN pipenv lock -r > requirements.txt

RUN pip install -r requirements.txt

CMD python -m foobartory.main