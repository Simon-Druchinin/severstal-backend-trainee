FROM python:3.11

RUN mkdir /fastapi_warehouse_app

WORKDIR /fastapi_warehouse_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
