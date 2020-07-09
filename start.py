#!/usr/bin/python

import os
import bme680
from influxdb import InfluxDBClient
import datetime
import time

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float(res.replace("temp=","").replace("'C\n", ""))

def get_temperature(sense):
    sense_temp = sense.data.temperature
    cpu_temp = get_cpu_temp()
    return sense_temp - ((cpu_temp - sense_temp) / 1.5)

try:
    try:
        sense = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except IOError:
	sense = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

    sense.set_humidity_oversample(bme680.OS_2X)
    sense.set_pressure_oversample(bme680.OS_4X)
    sense.set_temperature_oversample(bme680.OS_8X)
    sense.set_filter(bme680.FILTER_SIZE_3)
    sense.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sense.set_gas_heater_temperature(320)
    sense.set_gas_heater_duration(150)
    sense.select_gas_heater_profile(0)

    client = InfluxDBClient("localhost", 8086, "root", "root", "weather_node")

    start_time = time.time()
    current_time = time.time()
    burn_in_time = 300
    burn_in_data = []

    while current_time - start_time < burn_in_time:
        current_time = time.time()

        if sense.get_sensor_data() and sense.data.heat_stable:
            gas = sense.data.gas_resistance

	    burn_in_data.append(gas)
            time.sleep(1)

    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    humidity_baseline = 40.0
    humidity_weighting = 0.25

    while True:
        timestamp = datetime.datetime.utcnow().isoformat()

	if sense.get_sensor_data() and sense.data.heat_stable:
            temperature = sense.data.temperature
            pressure = sense.data.pressure

            gas = sense.data.gas_resistance
            gas_offset = gas_baseline - gas

            if gas_offset > 0:
                gas = (gas / gas_baseline)
                gas *= (100 - (humidity_weighting * 100))
            else:
                gas = 100 - (humidity_weighting * 100)

            humidity = sense.data.humidity
            humidity_offset = humidity - humidity_baseline

            if humidity_offset > 0:
                humidity = (100 - humidity_baseline - humidity_offset)
                humidity /= (100 - humidity_baseline)
                humidity *= (humidity_weighting * 100)
            else:
                humidity = (humidity_baseline + humidity_offset)
                humidity /= humidity_baseline
                humidity *= (humidity_weighting * 100)

            airquality = gas + humidity

            datapoints = [{
                "measurement": "office",
                "tags": {},
                "time": timestamp,
                "fields": {
                    "temperaturevalue": temperature,
                    "pressurevalue": pressure,
		    "gasvalue": gas,
                    "humidityvalue": humidity,
                    "airqualityvalue": airquality
                }
            }]

        client.write_points(datapoints)
except KeyboardInterrupt:
	print("Exit")
