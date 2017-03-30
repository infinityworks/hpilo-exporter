"""
Pulls data from specified iLO and presents as Prometheus metrics
"""

import hpilo

from tornado.gen import coroutine
from tornado.gen import Return
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler

class MainHandler(RequestHandler):
    """
    Redirect into the metrics endpoint
    """

    def get(self):
        self.redirect('/metrics')


class MetricsHandler(RequestHandler):
    """
    Endpoint handler
    """

    @coroutine
    def fetch_ilo_stats(self, ilo_host, ilo_port, ilo_user, ilo_password):
        """
        Fetch iLO stats endpoint, de-serialize JSON and return as Python dict

        0 - OK
        1 - Degraded
        2 - Dead (Other)

        :param ilo_host: ilo host
        :param ilo_port: ilo port
        :param ilo_user: ilo user
        :param ilo_password: ilo password
        :rtype: dict
        :return: ilo stats data
        """

        # if querystring param exists, overwrite the given value
        # TODO - improve where this code lives and DRY it out a bit
        query_ilo_host = self.get_query_arguments("ilo_host", strip=True)
        if query_ilo_host:
            ilo_host = ''.join(map(str, query_ilo_host))

        query_ilo_port = self.get_query_arguments("ilo_port", strip=True)
        if query_ilo_port:
            ilo_port = ''.join(map(str, query_ilo_port))

        query_ilo_user = self.get_query_arguments("ilo_user", strip=True)
        if query_ilo_user:
            ilo_user = ''.join(map(str, query_ilo_user))

        query_ilo_password = self.get_query_arguments("ilo_password", strip=True)
        if query_ilo_password:
            ilo_password = ''.join(map(str, query_ilo_password))

        data = {}
        try:
            data = hpilo.Ilo(hostname=ilo_host, login=ilo_user, password=ilo_password, timeout=10, port=int(ilo_port)).get_embedded_health()['health_at_a_glance']
        except (Exception) as e:
            print("Error fetching data from iLO (hostname=%s, login=%s, port=%s)") % (ilo_host, ilo_user, ilo_port)
            raise HTTPError(500, str(e))

        raise Return(data)

    def parse_ilo_stats_data(self, ilo_stats_data):
        """
        Filter key/values pairs from collected iLO stats and output as gauged Prometheus metrics

        :param ilo_stats_data: Collected iLO stats object
        :type ilo_stats_data: dict
        :return: Generator of metrics that can be put into Prometheus
        """

        for key, value in ilo_stats_data.items():

            for status in value.items():
                if status[0] == 'status':
                    if status[1] == 'OK':
                        gauge = 0
                    elif status[1] == 'Degraded':
                        gauge = 1
                    else:
                        gauge = 2

            if isinstance(gauge, (int, float, bool)):
                prom_value = float(gauge)
                prom_str = "hpilo_{} {}".format(key, prom_value)
                yield prom_str

    @coroutine
    def get(self):
        """
        Process GET request

        :return: Response with Prometheus metrics snapshot
        """

        # TODO time out the request at hpilo.Ilo(timeout=10)

        ilo_stats_data = yield self.fetch_ilo_stats(self.application.ilo_host, self.application.ilo_port, self.application.ilo_user, self.application.ilo_password)
        prometheus = "\n".join(self.parse_ilo_stats_data(ilo_stats_data)) + "\n"
        self.set_header("Content-Type", "text/plain")
        self.write(prometheus)

class iLOExporterServer(object):
    """
    Basic server implementation that exposes metrics to Prometheus fetcher.
    """

    # server config
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8080

    # exporter config
    DEFAULT_ILO_HOST = "127.0.0.1"
    DEFAULT_ILO_PORT = 443
    DEFAULT_ILO_USER = "admin"
    DEFAULT_ILO_PASSWORD = "admin"

    def __init__(self, address=None, port=None, ilo_host=None, ilo_port=None, ilo_user=None, ilo_password=None):
        self._address = address or self.DEFAULT_HOST
        self._port = port or self.DEFAULT_PORT
        self._ilo_host = ilo_host or self.DEFAULT_ILO_HOST
        self._ilo_port = ilo_port or self.DEFAULT_ILO_PORT
        self._ilo_user = ilo_user or self.DEFAULT_ILO_USER
        self._ilo_password = ilo_password or self.DEFAULT_ILO_PASSWORD

    def make_app(self):
        app = Application([
            (r"/", MainHandler),
            (r"/metrics", MetricsHandler),
        ])
        app.ilo_host = self._ilo_host
        app.ilo_port = self._ilo_port
        app.ilo_user = self._ilo_user
        app.ilo_password = self._ilo_password
        return app

    def print_info(self):
        print("Starting exporter on: http://%s:%s/metrics" % (self._address, self._port))
        print("Default iLO: %s@%s:%s" % (self._ilo_user, self._ilo_host, self._ilo_port))
        print("Press Ctrl+C to quit")

    def run(self):
        self.print_info()
        app = self.make_app()
        app.listen(self._port, address=self._address)
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            loop.stop()
