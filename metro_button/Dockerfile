FROM python:3.10.6-alpine

COPY requirements.txt .
RUN pip install --upgrade pip -r requirements.txt
RUN apt update && apt-get -y -v install libfbclient2

COPY .. .

EXPOSE 5000

#ENV FB_HOST=$FB_HOST
#ENV FB_DATABASE = $FB_DATABASE
#ENV FB_USER = $FB_USER
#ENV FB_PASSWORD = $FB_PASSWORD


CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]