FROM python:3.10.6

COPY requirements.txt .
RUN pip install --upgrade pip -r requirements.txt

COPY .. .

EXPOSE 5000

ENTRYPOINT ["./gunicorn.sh"]

#CMD ["python", "app.py"]