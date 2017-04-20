"""
Pulls data from specified iLO and presents as Prometheus metrics
"""
import hpilo
import prometheus_metrics
import sys

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn
from prometheus_client import Gauge
from prometheus_client import generate_latest
from urlparse import parse_qs
from urlparse import urlparse


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    max_children = 30
    timeout = 30


class RequestHandler(BaseHTTPRequestHandler):
    """
    Endpoint handler
    """

    def do_GET(self):
        """
        Process GET request

        :return: Response with Prometheus metrics
        """
        url = urlparse(self.path)

        query_components = parse_qs(urlparse(self.path).query)

        if url.path == '/metrics':

            query_ilo_host = query_components.get('ilo_host', [self.server.ilo_host])
            if query_ilo_host:
                ilo_host = query_ilo_host[0]

            query_ilo_port = query_components.get('ilo_port', [self.server.ilo_port])
            if query_ilo_port:
                ilo_port = int(query_ilo_port[0])

            query_ilo_user = query_components.get('ilo_user', [self.server.ilo_user])
            if query_ilo_user:
                ilo_user = query_ilo_user[0]

            query_ilo_password = query_components.get('ilo_password', [self.server.ilo_password])
            if query_ilo_password:
                ilo_password = query_ilo_password[0]

            data = {}
            try:
                data = hpilo.Ilo(hostname=ilo_host, login=ilo_user, password=ilo_password,
                                 port=ilo_port, timeout=10).get_embedded_health()['health_at_a_glance']

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

                metrics = generate_latest(prometheus_metrics.registry)

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(metrics)

            except:
                self.send_response(500)
                self.end_headers()

        elif url.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write("""<html>
            <head><title>HP iLO Exporter</title></head>
            <body>
            <h1>HP iLO Exporter</h1>
            <p>Visit <code>/metrics</code> to use.</p>
            </body>
            </html>""")

        else:
            self.send_response(404)
            self.end_headers()


class iLOExporterServer(object):
    """
    Basic server implementation that exposes metrics to Prometheus
    """

    def __init__(self, address, port, ilo_host, ilo_port, ilo_user, ilo_password):
        self._address = address
        self._port = port
        self._ilo_host = ilo_host
        self._ilo_port = ilo_port
        self._ilo_user = ilo_user
        self._ilo_password = ilo_password

    def print_info(self):
        print("Starting exporter on: http://{}:{}/metrics".format(self._address, self._port))
        print("Default iLO: {}@{}:{}".format(self._ilo_user, self._ilo_host, self._ilo_port))
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
