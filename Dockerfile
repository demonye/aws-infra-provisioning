FROM docker:18-dind

RUN apk update && apk add nodejs npm python3 py3-pip git jq
RUN npm install -g aws-cdk && cdk --version

RUN mkdir /app

WORKDIR /app
COPY requirements /app/requirements/
RUN pip3 install -r requirements/test.txt
RUN pip3 install git-remote-codecommit awscli
COPY aip /app/aip/

# unittests 
COPY tests /app/tests/

# integration tests 
COPY features /app/features/

COPY app.py cdk.json bin/deploy.sh bin/showdomain.py /app/
COPY demoapp /app/demoapp/
