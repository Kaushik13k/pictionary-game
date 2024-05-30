FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "main.py"]