#!/usr/bin/python

# -*- coding: utf-8 -*-

import argparse
import time
import datetime
import sys
from influxdb import InfluxDBClient
from sense_hat import SenseHat

sense = SenseHat()
sampling_period = 5

def get_data_points():
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
    
    return datapoints

# Initialize the Influxdb client

client = InfluxDBClient("localhost", 8086, "root", "root", "logger_db")

try:
     while True:
        datapoints = get_data_points()
        client.write_points(datapoints)

        sense.show_message("OK")
        time.sleep(5)
except KeyboardInterrupt:
    print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")