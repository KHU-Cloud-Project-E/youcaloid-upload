FROM python:3.10

COPY ./app/ /app

RUN apt-get update \
&& pip install --upgrade pip \
&& pip install Flask \
&& pip install pyyaml \
&& pip install requests 

CMD ["python3", "/app/upload.py"]

EXPOSE 5000