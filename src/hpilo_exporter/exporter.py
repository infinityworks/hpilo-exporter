"""
Pulls data from specified iLO and presents as Prometheus metrics
"""
from _socket import gaierror

import hpilo
import sys

import time
import prometheus_metrics
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn
from prometheus_client import generate_latest, Summary
from urlparse import parse_qs
from urlparse import urlparse

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary(
    'request_processing_seconds', 'Time spent processing request')


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    max_children = 30
    timeout = 30


class RequestHandler(BaseHTTPRequestHandler):
    """
    Endpoint handler
    """
    def return_error(self):
        self.send_response(500)
        self.end_headers()

    def do_GET(self):
        """
        Process GET request

        :return: Response with Prometheus metrics
        """
        start_time = time.time()
        url = urlparse(self.path)

        query_components = parse_qs(urlparse(self.path).query)

        if url.path == '/metrics':
            if all(v is None for v in [self.server.ilo_host, self.server.ilo_port, self.server.ilo_user,
                                       self.server.ilo_password]):
                print("Missing argument")
                self.return_error()
            else:
                ilo_host = None
                query_ilo_host = query_components.get('ilo_host', [self.server.ilo_host])
                if query_ilo_host:
                    ilo_host = query_ilo_host[0]

                ilo_port = None
                query_ilo_port = query_components.get('ilo_port', [self.server.ilo_port])
                if query_ilo_port:
                    ilo_port = int(query_ilo_port[0])

                ilo_user = None
                query_ilo_user = query_components.get('ilo_user', [self.server.ilo_user])
                if query_ilo_user:
                    ilo_user = query_ilo_user[0]

                ilo_password = None
                query_ilo_password = query_components.get('ilo_password', [self.server.ilo_password])
                if query_ilo_password:
                    ilo_password = query_ilo_password[0]

                data = None
                try:
                    data = hpilo.Ilo(hostname=ilo_host, login=ilo_user, password=ilo_password,
                                     port=ilo_port, timeout=10).get_embedded_health()['health_at_a_glance']
                except hpilo.IloLoginFailed:
                    print("ILO login failed")
                    self.return_error()
                except gaierror:
                    print("ILO invalid address or port")
                    self.return_error()
                except hpilo.IloCommunicationError, e:
                    print(e)

                if data is not None:
                    for key, value in data.items():
                        for status in value.items():
                            if status[0] == 'status':
                                gauge = 'hpilo_{}_gauge'.format(key)

                                if status[1] == 'OK':
                                    prometheus_metrics.gauges[gauge].set(0)
                                elif status[1] == 'Degraded':
                                    prometheus_metrics.gauges[gauge].set(1)
                                else:
                                    prometheus_metrics.gauges[gauge].set(2)

                    REQUEST_TIME.observe(time.time() - start_time)

                    metrics = generate_latest(prometheus_metrics.registry)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(metrics)

        elif url.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write("""<html>
            <head><title>HP iLO Exporter</title></head>
            <body>
            <h1>HP iLO Exporter</h1>
            <p>Visit <a href="/metrics">Metrics</a> to use.</p>
            </body>
            </html>""")

        else:
            self.send_response(404)
            self.end_headers()


class ILOExporterServer(object):
    """
    Basic server implementation that exposes metrics to Prometheus
    """

    def __init__(self, address=None, port=None, ilo_host=None, ilo_port=None, ilo_user=None, ilo_password=None):
        self._address = address
        if self._address is None:
            self._address = '0.0.0.0'
        self._port = port
        if self._port is None:
            self._port = 8080

        self._ilo_host = ilo_host
        self._ilo_port = ilo_port
        self._ilo_user = ilo_user
        self._ilo_password = ilo_password

    def print_info(self):
        print("Starting exporter on: http://{}:{}/metrics".format(self._address, self._port))
        print("Press Ctrl+C to quit")

    def run(self):
        self.print_info()

        server = ForkingHTTPServer((self._address, self._port), RequestHandler)

        server.ilo_host = self._ilo_host
        server.ilo_port = self._ilo_port
        server.ilo_user = self._ilo_user
        server.ilo_password = self._ilo_password

        try:
            while True:
                sys.stdout.flush()
                server.handle_request()
        except KeyboardInterrupt:
            print("Killing exporter")
            server.server_close()
