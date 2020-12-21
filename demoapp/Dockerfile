FROM python:3-alpine

RUN mkdir /app
WORKDIR /app
COPY main.py requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]
