FROM python:3-alpine

RUN mkdir /app
WORKDIR /app
RUN pip install fastapi uvicorn
COPY main.py .
EXPOSE 80

CMD ["uvicorn", "--port", "80", "main:app"]
