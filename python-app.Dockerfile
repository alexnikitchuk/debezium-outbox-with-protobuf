FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install --upgrade pip

COPY ./webapp .

RUN pip install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
