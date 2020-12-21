FROM docker:18-dind

RUN apk update && apk add nodejs npm python3 py3-pip git jq
RUN npm install -g aws-cdk && cdk --version

RUN mkdir /app

WORKDIR /app
COPY requirements /app/requirements/
RUN pip3 install -r requirements/prod.txt
RUN pip3 install git-remote-codecommit awscli
COPY aip /app/aip/
COPY tests /app/tests/
COPY app.py tasks.py cdk.json deploy.sh /app/
COPY demoapp /app/demoapp/
