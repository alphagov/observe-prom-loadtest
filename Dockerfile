FROM        python:2.7-slim
MAINTAINER  GDS Observe Team
ENV PROM_SERVER='https://prom-1.dj-test.dev.gds-reliability.engineering/'

RUN pip install locustio
RUN pip install prometheus_client
COPY locust-tools /locust-tools
COPY start.sh /start.sh
RUN touch /tmp/outfile && chmod +x /start.sh
CMD ["/start.sh"]