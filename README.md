# HP iLO Metrics Exporter

Exports HP Server Integrated Lights Out (iLO) heath_at_a_glance states to Prometheus gauges

```
0 - OK
1 - Degraded
2 - Dead (Other)
```

```
health_at_a_glance:
  battery: {status: OK}
  bios_hardware: {status: OK}
  fans: {redundancy: Redundant, status: OK}
  memory: {status: OK}
  network: {status: OK}
  power_supplies: {redundancy: Redundant, status: OK}
  processor: {status: OK}
  storage: {status: Degraded}
  temperature: {status: OK}
```

## Installing

You can install exporter on the server directly or on separate machine.
To run, you must have `Python` and `pip` installed.

To install with `pip`:

```
pip install hpilo-exporter
```

Then just:

```
hpilo-exporter --ilo-addr=127.0.0.1 --ilo-user=monitoring --ilo-password=monitoring
```

## Docker

To run the container, simply use the below:

`docker run -p 8080:8080 infinityworks/hpilo-exporter:latest --ilo-addr=127.0.0.1 --ilo-user=monitoring --ilo-password=monitoring`

Example Docker Compose:

```
  hpilo-exporter:
    command: --ilo-addr=127.0.0.1 --ilo-user=monitoring --ilo-password=monitoring
    image: infinityworks/hpilo-exporter:latest
    ports:
    - "8080:8080"
```

## TODO

- Break out iLO config so we can specify a range of servers
  - Need to be aware of how Prometheus can call specific servers, maybe query string params
