FROM python:3.8-alpine

RUN apk update && apk add nodejs npm
RUN npm install -g aws-cdk && cdk --version

RUN mkdir /app

WORKDIR /app
COPY requirements /app/requirements/
RUN pip install -r requirements/prod.txt
COPY aip /app/aip/
COPY tests /app/tests/
COPY app.py tasks.py cdk.json /app/

CMD ["invoke", "deploy"]
