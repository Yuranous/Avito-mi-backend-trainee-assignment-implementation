FROM python:3.8.6-buster
COPY . /app
WORKDIR app
RUN pip install -r requirements.txt
CMD python app.py