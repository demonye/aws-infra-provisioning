FROM python:3.8-alpine

RUN apk update && apk add nodejs npm
RUN npm install -g aws-cdk && cdk --version

RUN mkdir /app
WORKDIR /app
COPY app.py cdk.json src requirements tests .
RUN pip install -r requirements/prod.txt && rm -rf requirements

CMD ["cdk", "--help"]
