from prometheus_client import Gauge, Summary
from prometheus_client import REGISTRY

registry = REGISTRY

hpilo_battery_gauge = Gauge('hpilo_battery', 'HP iLO battery status')
hpilo_storage_gauge = Gauge('hpilo_storage', 'HP iLO storage status')
hpilo_fans_gauge = Gauge('hpilo_fans', 'HP iLO fans status')
hpilo_bios_hardware_gauge = Gauge('hpilo_bios_hardware', 'HP iLO bios_hardware status')
hpilo_memory_gauge = Gauge('hpilo_memory', 'HP iLO memory status')
hpilo_power_supplies_gauge = Gauge('hpilo_power_supplies', 'HP iLO power_supplies status')
hpilo_processor_gauge = Gauge('hpilo_processor', 'HP iLO processor status')
hpilo_network_gauge = Gauge('hpilo_network', 'HP iLO network status')
hpilo_temperature_gauge = Gauge('hpilo_temperature', 'HP iLO temperature status')

gauges = {
    'hpilo_battery_gauge': hpilo_battery_gauge,
    'hpilo_storage_gauge': hpilo_storage_gauge,
    'hpilo_fans_gauge': hpilo_fans_gauge,
    'hpilo_bios_hardware_gauge': hpilo_bios_hardware_gauge,
    'hpilo_memory_gauge': hpilo_memory_gauge,
    'hpilo_power_supplies_gauge': hpilo_power_supplies_gauge,
    'hpilo_processor_gauge': hpilo_processor_gauge,
    'hpilo_network_gauge': hpilo_network_gauge,
    'hpilo_temperature_gauge': hpilo_temperature_gauge,
}
