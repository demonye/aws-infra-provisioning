FROM python:3-alpine

RUN mkdir /app
WORKDIR /app
COPY main.py config.json requirements.txt ./
RUN pip install -r requirements.txt
EXPOSE 80

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "80", "main:app"]
