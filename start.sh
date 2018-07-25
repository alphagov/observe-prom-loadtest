#!/bin/bash
python /locust-tools/locustfile.py
locust -f /locust-tools/locustfile.py --host=$PROM_SERVER 
