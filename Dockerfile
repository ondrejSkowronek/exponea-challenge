FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r reqs.txt

CMD ["python", "exponea/manage.py", "runserver", "0.0.0.0:80"]
