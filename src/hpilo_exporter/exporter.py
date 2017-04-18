"""
Pulls data from specified iLO and presents as Prometheus metrics
"""
import hpilo
import prometheus_metrics
import sys
import traceback

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn
from prometheus_client import Gauge
from prometheus_client import generate_latest
from urlparse import parse_qs
from urlparse import urlparse


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    pass


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

            query_ilo_host = query_components.get(
                'ilo_host', self.server.ilo_host)
            if query_ilo_host:
                ilo_host = ''.join(map(str, query_ilo_host))

            query_ilo_port = query_components.get(
                'ilo_port', self.server.ilo_port)
            if query_ilo_port:
                ilo_port = ''.join(map(str, query_ilo_port))

            query_ilo_user = query_components.get(
                'ilo_user', self.server.ilo_user)
            if query_ilo_user:
                ilo_user = ''.join(map(str, query_ilo_user))

            query_ilo_password = query_components.get(
                'ilo_password', self.server.ilo_password)
            if query_ilo_password:
                ilo_password = ''.join(map(str, query_ilo_password))

            data = {}
            try:
                data = hpilo.Ilo(hostname=ilo_host, login=ilo_user, password=ilo_password, timeout=10, port=int(
                    ilo_port)).get_embedded_health()['health_at_a_glance']

                for key, value in data.items():
                    for status in value.items():
                        if status[0] == 'status':
                            gauge = 'hpilo_' + key + '_gauge'

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
                self.wfile.write(traceback.format_exc())

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
    Basic server implementation that exposes metrics to Prometheus fetcher.
    """

    # server config
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8080

    # exporter config
    DEFAULT_ILO_HOST = "127.0.0.1"
    DEFAULT_ILO_PORT = "443"
    DEFAULT_ILO_USER = "user"
    DEFAULT_ILO_PASSWORD = "pass"

    def __init__(self, address=None, port=None, ilo_host=None, ilo_port=None, ilo_user=None, ilo_password=None):
        self._address = address or self.DEFAULT_HOST
        self._port = port or self.DEFAULT_PORT
        self._ilo_host = ilo_host or self.DEFAULT_ILO_HOST
        self._ilo_port = ilo_port or self.DEFAULT_ILO_PORT
        self._ilo_user = ilo_user or self.DEFAULT_ILO_USER
        self._ilo_password = ilo_password or self.DEFAULT_ILO_PASSWORD

    def print_info(self):
        print("Starting exporter on: http://%s:%s/metrics" %
              (self._address, self._port))
        print("Default iLO: %s@%s:%s" %
              (self._ilo_user, self._ilo_host, self._ilo_port))
        print("Press Ctrl+C to quit")

    def run(self):
        self.print_info()

        server = ForkingHTTPServer(
            (self._address, self._port), RequestHandler)

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
