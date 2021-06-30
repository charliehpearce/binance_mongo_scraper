FROM python:3.9-alpine
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "./scraper.py"]
