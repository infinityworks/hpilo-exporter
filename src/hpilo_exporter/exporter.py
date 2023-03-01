"""
Pulls data from specified iLO and presents as Prometheus metrics
"""
from __future__ import print_function
from _socket import gaierror
import sys
import hpilo

import time
import prometheus_metrics
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn
from prometheus_client import generate_latest, Summary
from urlparse import parse_qs
from urlparse import urlparse


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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
        # this will be used to return the total amount of time the request took
        start_time = time.time()
        # get parameters from the URL
        url = urlparse(self.path)
        # following boolean will be passed to True if an error is detected during the argument parsing
        error_detected = False
        query_components = parse_qs(urlparse(self.path).query)

        ilo_host = None
        ilo_port = None
        ilo_user = None
        ilo_password = None
        try:
            ilo_host = query_components['ilo_host'][0]
            ilo_port = int(query_components['ilo_port'][0])
            ilo_user = query_components['ilo_user'][0]
            ilo_password = query_components['ilo_password'][0]
        except KeyError, e:
            print_err("missing parameter %s" % e)
            self.return_error()
            error_detected = True

        if url.path == self.server.endpoint and ilo_host and ilo_user and ilo_password and ilo_port:

            ilo = None
            try:
                ilo = hpilo.Ilo(hostname=ilo_host,
                                login=ilo_user,
                                password=ilo_password,
                                port=ilo_port, timeout=10)
            except hpilo.IloLoginFailed:
                print("ILO login failed")
                self.return_error()
            except gaierror:
                print("ILO invalid address or port")
                self.return_error()
            except hpilo.IloCommunicationError, e:
                print(e)

            # get product and server name
            try:
                product_name = ilo.get_product_name()
            except:
                product_name = "Unknown HP Server"

            try:
                server_name = ilo.get_server_name()
                if server_name == "":
                    server_name = ilo_host
            except:
                server_name = ilo_host


            # get health
            embedded_health = ilo.get_embedded_health()
            health_at_glance = embedded_health['health_at_a_glance']

            for module in embedded_health['temperature'].values():
                if module['status'] != 'Not Installed':
                    prometheus_metrics.gauges["hpilo_temperature_detail_gauge"].labels(label=module['label'], product_name=product_name, server_name=server_name).set(int(module['currentreading'][0]))

            present_power_reading = int(embedded_health['power_supply_summary']['present_power_reading'].split()[0])
            prometheus_metrics.gauges["hpilo_power_supplies_reading_gauge"].labels(product_name=product_name, server_name=server_name).set(present_power_reading)

            for fan in embedded_health['fans'].values():
                prometheus_metrics.gauges["hpilo_fans_speed_percent_gauge"].labels(fan_status=fan['status'], fan_name=fan['label'], fan_id=fan['label'].split()[-1], product_name=product_name, server_name=server_name).set(0 if present_power_reading == 0 else int(fan['speed'][0]))

            memory_detail = embedded_health['memory']['memory_details_summary'] if 'memory_details_summary' in embedded_health['memory'] else embedded_health['memory']['memory_components']

            # For HP server Gen 8 or lower
            if 'memory_details_summary' in embedded_health['memory']:
                for cpu_idx, cpu in memory_detail.items():
                    total_memory_size = 0 if (cpu['total_memory_size'] == 'N/A') else int(cpu['total_memory_size'].split()[0])
                    prometheus_metrics.gauges["hpilo_memory_detail_gauge"].labels(product_name=product_name, server_name=server_name, cpu_id=cpu_idx.split("_")[1], operating_frequency=cpu['operating_frequency'], operating_voltage=cpu['operating_voltage']).set(total_memory_size)

            # For HP server Gen 9 or higher
            if 'memory_components' in embedded_health['memory']:
                memory_components = embedded_health['memory']['memory_components']
                for cpu_idx in range(0, len(memory_components)):
                    cpu = memory_components[cpu_idx]
                    total_memory_size = 0 if (cpu[1][1]['value'] == 'Not Installed') else int(cpu[1][1]['value'].split(' ')[0]) / 1024
                    operating_frequency = cpu[2][1]['value']
                    # Not expose operating_voltage
                    prometheus_metrics.gauges["hpilo_memory_detail_gauge"].labels(product_name=product_name, server_name=server_name, cpu_id=cpu_idx, operating_frequency=operating_frequency, operating_voltage='').set(total_memory_size)

            for psu in embedded_health['power_supplies'].values():
                capacity_w = 0 if psu["capacity"] == "N/A" else int(psu["capacity"].split()[0])
                prometheus_metrics.gauges["hpilo_power_supplies_detail_gauge"].labels(product_name=product_name, server_name=server_name, psu_id=psu['label'].split()[-1], label=psu['label'], status=psu['status'], capacity_w=capacity_w, present=psu["present"]).set(1 if "Good" in psu["status"] else 0)

            for cpu in embedded_health['processors'].values():
                prometheus_metrics.gauges["hpilo_processor_detail_gauge"].labels(product_name=product_name, server_name=server_name, cpu_id=cpu['label'].split()[1], name=cpu['name'].strip(), status=cpu['status'], speed=cpu['speed']).set(1 if "OK" in cpu["status"] else 0)

            if health_at_glance is not None:
                for key, value in health_at_glance.items():

                    for status in value.items():
                        if status[0] == 'status':
                            gauge = 'hpilo_{}_gauge'.format(key)
                            if status[1].upper() == 'OK':
                                prometheus_metrics.gauges[gauge].labels(product_name=product_name,server_name=server_name).set(0)
                            elif status[1].upper() == 'DEGRADED':
                                prometheus_metrics.gauges[gauge].labels(product_name=product_name,server_name=server_name).set(1)
                            else:
                                prometheus_metrics.gauges[gauge].labels(product_name=product_name,server_name=server_name).set(2)

            #for iLO3 patch network
            if ilo.get_fw_version()["management_processor"] == 'iLO3':
                print_err('Unknown iLO nic status')
            else:
                # get nic information
                for nic_name,nic in embedded_health['nic_information'].items():
                   try:
                       value = ['OK','Disabled','Unknown','Link Down'].index(nic['status'])
                   except ValueError:
                       value = 4
                       print_err('unrecognised nic status: {}'.format(nic['status']))

                   prometheus_metrics.hpilo_nic_status_gauge.labels(product_name=product_name,
                                                                    server_name=server_name,
                                                                    nic_name=nic_name,
                                                                    ip_address=nic['ip_address']).set(value)

            # get firmware version
            fw_version = ilo.get_fw_version()["firmware_version"]
            # prometheus_metrics.hpilo_firmware_version.set(fw_version)
            prometheus_metrics.hpilo_firmware_version.labels(product_name=product_name,
                                                             server_name=server_name).set(fw_version)

            # get the amount of time the request took
            REQUEST_TIME.observe(time.time() - start_time)

            # generate and publish metrics
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
            if not error_detected:
                self.send_response(404)
                self.end_headers()


class ILOExporterServer(object):
    """
    Basic server implementation that exposes metrics to Prometheus
    """

    def __init__(self, address='0.0.0.0', port=8080, endpoint="/metrics"):
        self._address = address
        self._port = port
        self.endpoint = endpoint

    def print_info(self):
        print_err("Starting exporter on: http://{}:{}{}".format(self._address, self._port, self.endpoint))
        print_err("Press Ctrl+C to quit")

    def run(self):
        self.print_info()

        server = ForkingHTTPServer((self._address, self._port), RequestHandler)
        server.endpoint = self.endpoint

        try:
            while True:
                server.handle_request()
        except KeyboardInterrupt:
            print_err("Killing exporter")
            server.server_close()
