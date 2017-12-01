"""
Entrypoint for the application
"""

import argparse

from hpilo_exporter.exporter import ILOExporterServer


def main():
    parser = argparse.ArgumentParser(description='Exports ilo heath_at_a_glance state to Prometheus')

    parser.add_argument('--address', type=str, dest='address', default='0.0.0.0', help='address to serve on')
    parser.add_argument('--port', type=int, dest='port', default='8080', help='port to bind')
    parser.add_argument('--ilo-host', type=str, dest='ilo_host', default='127.0.0.1', help='iLO hostname/ip')
    parser.add_argument('--ilo-port', type=int, dest='ilo_port', default='443', help='iLO port')
    parser.add_argument('--ilo-user', type=str, dest='ilo_user', default='user', help='iLO user')
    parser.add_argument('--ilo-password', type=str, dest='ilo_password', default='pass', help='iLO password')

    args = parser.parse_args()

    exporter = ILOExporterServer(**vars(args))
    exporter.run()


if __name__ == '__main__':
    main()
