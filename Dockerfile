FROM python:3

WORKDIR  /usr/src/app

RUN pip install flask
RUN pip install flask_socketio

COPY . .

CMD ["python", "./app.py"]
