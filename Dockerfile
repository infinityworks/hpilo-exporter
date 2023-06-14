FROM python:3.11-alpine
ADD . /usr/src/hpilo_exporter
RUN pip install -e /usr/src/hpilo_exporter
ENTRYPOINT ["/usr/local/bin/python", "-m", "hpilo_exporter"]
EXPOSE 9416
