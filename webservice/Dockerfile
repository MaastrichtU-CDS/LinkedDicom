FROM python:3.8-buster

RUN mkdir /app
COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt
COPY ./LinkedDicom.owl /app/LinkedDicom.owl

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 80
CMD ["python", "app.py"]