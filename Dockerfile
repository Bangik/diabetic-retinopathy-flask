FROM python:3.9.7-slim-buster

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6  -y

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]