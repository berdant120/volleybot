FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt
COPY src ./src

CMD python src/app.py
