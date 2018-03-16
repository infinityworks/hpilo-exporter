FROM python:2.7-alpine
ADD . /usr/src/hpilo_exporter
RUN pip install -e /usr/src/hpilo_exporter
ENTRYPOINT ["hpilo-exporter"]
EXPOSE 9416
