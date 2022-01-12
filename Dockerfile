FROM python:3.10-alpine
ADD . /usr/src/hpilo_exporter
RUN pip install -e /usr/src/hpilo_exporter
ENTRYPOINT ["hpilo-exporter"]
EXPOSE 9416
