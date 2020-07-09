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
    sense_temp = sense.get_temperature()
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

    client = InfluxDBClient("localhost", 8086, "root", "root", "weather_node")

    while True:
        timestamp = datetime.datetime.utcnow().isoformat()

	if sense.get_sensor_data():
            temperature = sense.data.temperature
            humidity = sense.data.humidity
            pressure = sense.data.pressure

            datapoints = [{
                "measurement": "office",
                "tags": {},
                "time": timestamp,
                "fields": {
                    "temperaturevalue": temperature,
                    "humidityvalue": humidity,
                    "pressurevalue": pressure
                }
            }]

        client.write_points(datapoints)
except KeyboardInterrupt:
	print("Exit")
