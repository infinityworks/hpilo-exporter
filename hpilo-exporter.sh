#!/bin/bash

# create user
useradd --no-create-home --shell /bin/false hpilo_exporter


echo '[Unit]
Description=hpilo Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=hpilo_exporter
Group=hpilo_exporter
Type=simple
ExecStart=/usr/local/bin/hpilo-exporter  \
--address=0.0.0.0 \
--port=9416  \
--endpoint='/metrics'

[Install]
WantedBy=multi-user.target' > /etc/systemd/system/hpilo_exporter.service

# enable haproxy_exporter in systemctl
systemctl daemon-reload
systemctl start hpilo_exporter
systemctl enable hpilo_exporter


echo "Setup complete.
Add the following lines to /etc/prometheus/prometheus.yml:

  - job_name: 'hpilo'
  scrape_interval: 1m
  scrape_timeout: 30s
  params:
    ilo_port: ['443']
    ilo_user: ['my_ilo_user']
    ilo_password: ['my_ilo_password']
  static_configs:
    - targets:
      - ilo_fqdn.domain

  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_ilo_host
    - source_labels: [__param_ilo_host]
      target_label: ilo_host
    - target_label: __address__
      replacement: ip:9416  # hpilo exporter.
"

