FROM python_fb

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY .. .

EXPOSE 5000

ENV FB_HOST=$FB_HOST
ENV FB_DATABASE=$FB_DATABASE
ENV FB_USER=$FB_USER
ENV FB_PASSWORD=$FB_PASSWORD
ENV CHARSET=$CHARSET


CMD ["python", "app.py"]