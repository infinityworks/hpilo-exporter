# HP iLO Metrics Exporter

Exports HP Server Integrated Lights Out (iLO) heath_at_a_glance states to Prometheus gauges, from either a single server (via command line flags) or multiple servers (via query string parameters)

### Gauges

```
0 - OK
1 - Degraded
2 - Dead (Other)
```

### iLO

```
health_at_a_glance:
  battery: {status: OK}
  bios_hardware: {status: OK}
  fans: {redundancy: Redundant, status: OK}
  memory: {status: OK}
  network: {status: Link Down},
  power_supplies: {redundancy: Redundant, status: OK}
  processor: {status: OK}
  storage: {status: Degraded}
  temperature: {status: OK}
```

### Output

```
hpilo_battery 0.0
hpilo_storage 1.0
hpilo_fans 0.0
hpilo_bios_hardware 0.0
hpilo_memory 0.0
hpilo_power_supplies 0.0
hpilo_processor 0.0
hpilo_network 2.0
hpilo_temperature 0.0
```

## Installing

You can install exporter on the server directly or on separate machine.
To run, you must have `Python` and `pip` installed.

To install with `pip`:

```
pip install -e $HPILO_EXPORTER_DIR
```

Then just:

```
hpilo-exporter [--address=0.0.0.0 --port=8080 --ilo-host=127.0.0.1 --ilo-port=443 --ilo-user=monitoring --ilo-password=monitoring]
```

## Docker

To run the container, assuming it has been built locally:

`docker run -p 8080:8080 hpilo-exporter:latest --ilo-addr=127.0.0.1 --ilo-user=monitoring --ilo-password=monitoring`

Example Docker Compose:

```
  hpilo-exporter:
    command: --address=0.0.0.0 --port=8080 --ilo-host=127.0.0.1 --ilo-port=443 --ilo-user=monitoring --ilo-password=monitoring
    image: hpilo-exporter:latest
    ports:
    - "8080:8080"
```

## Multi iLO communication

Using query string parameters to the `/metrics` endpoint you can point the exporter to different iLO's

```
curl 'http://127.0.0.1:8080/metrics?ilo_host=127.0.0.1&ilo_port=9018&ilo_user=admin&ilo_password=admin'
```
