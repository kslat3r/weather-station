#!/usr/bin/python

# -*- coding: utf-8 -*-

import time
import datetime
from influxdb import InfluxDBClient
from sense_hat import SenseHat

sense = SenseHat()
client = InfluxDBClient("localhost", 8086, "root", "root", "logger_db")

try:
     while True:
        temperature = sense.get_temperature()
        pressure = sense.get_pressure()
        humidity = sense.get_humidity()
        timestamp = datetime.datetime.utcnow().isoformat()
        
        datapoints = [{
            "measurement": "test1",
            "tags": {},
            "time": timestamp,
            "fields": {
                "temperaturevalue": temperature,
                "pressurevalue": pressure,
                "humidityvalue": humidity
            }
        }]
        
        client.write_points(datapoints)

        sense.show_message("OK")
        
        time.sleep(5)
except KeyboardInterrupt:
    print("Exit")