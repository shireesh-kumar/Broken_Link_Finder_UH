FROM python:3.13-slim-bullseye

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "./broken_link_finder.py"]

