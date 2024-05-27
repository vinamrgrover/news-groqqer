FROM python:3.12

WORKDIR ./app

COPY ./src/*.py .
COPY ./src/requirements.txt .
COPY ./src/.env .

RUN pip install -r requirements.txt

CMD [ "python", "runner.py" ]