from prometheus_client import Gauge
from prometheus_client import REGISTRY

registry = REGISTRY

hpilo_vrm_gauge = Gauge('hpilo_vrm', 'HP iLO vrm status', ["product_name", "server_name"])
hpilo_drive_gauge = Gauge('hpilo_drive', 'HP iLO drive status', ["product_name", "server_name"])
hpilo_battery_gauge = Gauge('hpilo_battery', 'HP iLO battery status', ["product_name", "server_name"])
hpilo_storage_gauge = Gauge('hpilo_storage', 'HP iLO storage status', ["product_name", "server_name"])
hpilo_fans_gauge = Gauge('hpilo_fans', 'HP iLO fans status', ["product_name", "server_name"])
hpilo_bios_hardware_gauge = Gauge('hpilo_bios_hardware', 'HP iLO bios_hardware status', ["product_name", "server_name"])
hpilo_memory_gauge = Gauge('hpilo_memory', 'HP iLO memory status', ["product_name", "server_name"])
hpilo_power_supplies_gauge = Gauge('hpilo_power_supplies', 'HP iLO power_supplies status', ["product_name",
                                                                                            "server_name"])
hpilo_processor_gauge = Gauge('hpilo_processor', 'HP iLO processor status', ["product_name", "server_name"])
hpilo_network_gauge = Gauge('hpilo_network', 'HP iLO network status', ["product_name", "server_name"])
hpilo_temperature_gauge = Gauge('hpilo_temperature', 'HP iLO temperature status', ["product_name", "server_name"])
hpilo_firmware_version = Gauge('hpilo_firmware_version', 'HP iLO firmware version', ["product_name", "server_name"])

gauges = {
    'hpilo_vrm_gauge': hpilo_vrm_gauge,
    'hpilo_drive_gauge': hpilo_drive_gauge,
    'hpilo_battery_gauge': hpilo_battery_gauge,
    'hpilo_storage_gauge': hpilo_storage_gauge,
    'hpilo_fans_gauge': hpilo_fans_gauge,
    'hpilo_bios_hardware_gauge': hpilo_bios_hardware_gauge,
    'hpilo_memory_gauge': hpilo_memory_gauge,
    'hpilo_power_supplies_gauge': hpilo_power_supplies_gauge,
    'hpilo_processor_gauge': hpilo_processor_gauge,
    'hpilo_network_gauge': hpilo_network_gauge,
    'hpilo_temperature_gauge': hpilo_temperature_gauge,
    'hpilo_firmware_version': hpilo_firmware_version,
}
