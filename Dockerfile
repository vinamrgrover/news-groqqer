FROM python:3.12

WORKDIR ./app

COPY *.py .
COPY ./requirements.txt .
COPY ./.env .

RUN pip install -r requirements.txt

CMD [ "python", "runner.py" ]