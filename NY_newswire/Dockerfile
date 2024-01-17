FROM python:3.8-slim-bullseye
WORKDIR /newswire
ADD nyt_newswire.py /newswire/nyt_newswire.py
ADD requirements.txt /newswire/requirements.txt
RUN pip install -r requirements.txt
CMD python3 nyt_newswire.py