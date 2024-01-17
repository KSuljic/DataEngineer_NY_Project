FROM python:3.8-slim-bullseye
WORKDIR /dash
ADD web_gui.py /dash/web_gui.py
ADD requirements.txt /dash/requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8050
CMD python3 web_gui.py