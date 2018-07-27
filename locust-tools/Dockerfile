FROM        python:2.7-slim
MAINTAINER  GDS Observe Team
ENV PROM_SERVER='https://prom-1.dj-test.dev.gds-reliability.engineering/'

RUN pip install locustio
RUN pip install prometheus_client
COPY locust_exporter.py /locust_exporter.py
CMD ["python","/locust_exporter.py","4455","locustserver:8089"]
