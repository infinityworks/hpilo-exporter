"""
Entrypoint for the application
"""

import argparse

from hpilo_exporter import iLOExporterServer

def main():
    # Add some args config
    parser = argparse.ArgumentParser(description='Exports ilo heath_at_a_glance state to prometheus')
    parser.add_argument('--address', dest='address', help='address to serve on')
    parser.add_argument('--port', dest='port', help='port to bind')
    parser.add_argument('--ilo-host', dest='ilo_host', help='iLO hostname/ip')
    parser.add_argument('--ilo-port', dest='ilo_port', help='iLO port')
    parser.add_argument('--ilo-user', dest='ilo_user', help='iLO user')
    parser.add_argument('--ilo-password', dest='ilo_password', help='iLO password')
    args = parser.parse_args()

    # Run exposing server
    exposer = iLOExporterServer(**vars(args))
    exposer.run()
