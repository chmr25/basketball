FROM python:3.8-slim

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /opt/dagster/app/

RUN pip install --upgrade pip

RUN apt-get -y install libc6

RUN pip install psycopg2-binary

COPY requirements.txt /opt/dagster/app/

RUN pip install -r requirements.txt

COPY src/ /opt/dagster/app/src

WORKDIR /opt/dagster/app/

EXPOSE 4005

CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4005", "-f", "src/repository.py"]
