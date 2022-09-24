
# Diabetic Retinopathy Detection API using Flask

Requirement

Python 3.7

## How to Install and Run Localy

Clone from github
```bash
  git clone https://github.com/Bangik/diabetic-retinopathy-flask.git
```

Create an environment
```bash
  py -3 -m venv venv
```

Activate the environment
```bash
  venv\Scripts\activate
```

Install modules
```bash
  pip install -r requirements.txt
```

Run app
```bash
  flask --app main run
```

## How to run on Docker

Build Image

```bash
  docker image build -t dr-flask .
```

Run Image on Container

```bash
  docker run --name dr-flask-server -p 5000:5000 -d dr-flask
```