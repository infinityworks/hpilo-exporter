from prometheus_client import Gauge
from prometheus_client import REGISTRY

registry = REGISTRY

hpilo_vrm_gauge = Gauge('hpilo_vrm', 'HP iLO vrm status', ["product_name", "server_name"])
hpilo_drive_gauge = Gauge('hpilo_drive', 'HP iLO drive status', ["product_name", "server_name"])
hpilo_battery_gauge = Gauge('hpilo_battery', 'HP iLO battery status', ["product_name", "server_name"])
hpilo_storage_gauge = Gauge('hpilo_storage', 'HP iLO storage status', ["product_name", "server_name"])
hpilo_fans_gauge = Gauge('hpilo_fans', 'HP iLO fans status', ["product_name", "server_name"])
hpilo_fans_speed_percent_gauge = Gauge('hpilo_fans_speed_percent', 'HP iLO fans speed percent', ["product_name", "server_name", "fan_name", "fan_id", "fan_status"])
hpilo_bios_hardware_gauge = Gauge('hpilo_bios_hardware', 'HP iLO bios_hardware status', ["product_name", "server_name"])
hpilo_memory_gauge = Gauge('hpilo_memory', 'HP iLO memory status', ["product_name", "server_name"])
hpilo_memory_detail_gauge = Gauge('hpilo_memory_detail', 'HP iLO memory detail info', ["product_name", "server_name", "cpu_id", "operating_frequency", "operating_voltage"])
hpilo_power_supplies_gauge = Gauge('hpilo_power_supplies', 'HP iLO power_supplies status', ["product_name","server_name"])
hpilo_power_supplies_detail_gauge = Gauge('hpilo_power_supplies_detail', 'HP iLO power_supplies detail', ["product_name","server_name", "psu_id", "label", "status", "capacity_w", "present"])
hpilo_power_supplies_reading_gauge = Gauge('hpilo_power_supplies_reading', 'HP iLO power_supplies reading', ["product_name","server_name"])
hpilo_processor_gauge = Gauge('hpilo_processor', 'HP iLO processor status', ["product_name", "server_name"])
hpilo_processor_detail_gauge = Gauge('hpilo_processor_detail', 'HP iLO processor detail', ["product_name", "server_name", "name", "status", "cpu_id", "speed"])
hpilo_network_gauge = Gauge('hpilo_network', 'HP iLO network status', ["product_name", "server_name"])
hpilo_temperature_gauge = Gauge('hpilo_temperature', 'HP iLO temperature status', ["product_name", "server_name"])
hpilo_temperature_detail_gauge = Gauge('hpilo_temperature_detail', 'HP iLO temperature detail', ["product_name", "server_name", "label"])
hpilo_firmware_version = Gauge('hpilo_firmware_version', 'HP iLO firmware version', ["product_name", "server_name"])

hpilo_nic_status_gauge = Gauge('hpilo_nic_status_gauge', 'HP iLO NIC status', ["product_name", "server_name", "nic_name", "ip_address"])

gauges = {
    'hpilo_vrm_gauge': hpilo_vrm_gauge,
    'hpilo_drive_gauge': hpilo_drive_gauge,
    'hpilo_battery_gauge': hpilo_battery_gauge,
    'hpilo_storage_gauge': hpilo_storage_gauge,
    'hpilo_fans_gauge': hpilo_fans_gauge,
    'hpilo_fans_speed_percent_gauge': hpilo_fans_speed_percent_gauge,
    'hpilo_bios_hardware_gauge': hpilo_bios_hardware_gauge,
    'hpilo_memory_gauge': hpilo_memory_gauge,
    'hpilo_memory_detail_gauge': hpilo_memory_detail_gauge,
    'hpilo_power_supplies_gauge': hpilo_power_supplies_gauge,
    'hpilo_power_supplies_detail_gauge': hpilo_power_supplies_detail_gauge,
    'hpilo_power_supplies_reading_gauge': hpilo_power_supplies_reading_gauge,
    'hpilo_processor_gauge': hpilo_processor_gauge,
    'hpilo_processor_detail_gauge': hpilo_processor_detail_gauge,
    'hpilo_network_gauge': hpilo_network_gauge,
    'hpilo_temperature_gauge': hpilo_temperature_gauge,
    'hpilo_temperature_detail_gauge': hpilo_temperature_detail_gauge,
    'hpilo_firmware_version': hpilo_firmware_version,
    'hpilo_nic_status_gauge': hpilo_nic_status_gauge,
}
