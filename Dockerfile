FROM python:3.8
COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /
WORKDIR /src

CMD [ "python3", "-u", "main.py" ]