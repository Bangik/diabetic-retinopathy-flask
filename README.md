
# Diabetic Retinopathy Detection API using Flask

Requirement

Python >=3.7

## How to Install and Run Localy on Windows

Clone from github
```bash
  git clone https://github.com/Bangik/diabetic-retinopathy-flask.git
```

Create an environment
```bash
  python -m venv venv
```

Activate the environment
```bash
  venv\Scripts\activate
```

Install modules
```bash
  pip install -r requirements.txt
```

Copy .env.example and rename it to .env and edit
```bash
  cp .env.example .env
```

Run app
```bash
  flask --app app run
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