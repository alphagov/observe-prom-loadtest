Prometheus load tester for GDS RE Observe
=========================================
Tool using [Locust](https://locust.io/), Prometheus and Grafana to load test our Prometheus service.

First, we use Locust to query the Prometheus under test to find out which timeseries it has stored. It extracts a list
of these in order to generate a list of queries that can be used during the load test.

We then use Locust to load test the Prometheus.

We run an additional Prometheus which will scrape metrics from the Prometheus under test so we can see how it is handling the
load. We also run a (locustexporter)[https://github.com/mbolek/locust_exporter] which exposes metrics for Locust. These are then both graphed in a Grafana instance.


## Deployment method (Assuming that you already have a load test target)

### Set up a server in AWS (optional if running locally)

a. Boot a machine with the appropriate resources

b. Optional, If you want persistence then attach a disk to the machine. The disk should be formated according to your requirments

c.  Enusre that docker is installed on the system including docker compose

    curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose

d. Make sure that this repository is cloned on to the machine

### Set the location of the Prometheus under test

a. Once logged into to the machine, navigate to the cloned project repository

b. Configure the service by editing the 'locustfile.py' by setting the prometheus URL to your prometheus URL server.

```
metrics = find_metrics('https://prom-1.dj-test.dev.gds-reliability.engineering/', 'prometheus')
```

You also need to edit the variable in the docker file.

```
ENV PROM_SERVER='https://prom-1.dj-test.dev.gds-reliability.engineering/'
```

c. If accessing the prometheus under test requires authentication, e.g. basic auth, you need to edit the locust file using [these instructions](http://docs.python-requests.org/en/master/user/authentication/#basic-authentication)

d. Please also make sure that you configure prometheus to scrape the prometheus under test. This is done by adding the target prometheus server to the scrape config defined in `config/prometheus-config.yaml`.

### Build the project

a. Build the initial containers with the following commands:

    docker build -t local/locustserver .
    cd locust-tools
    docker build -t local/locustexporter .
    cd ..

b. Run the `docker-compose` command that should bring everything up as expected. You may need to run this as root as we have seen some issues with it.

    sudo docker-compose -f compose-env.yaml up

c. All should of gone well. You can verify this by running the following command and receiving similar output.

    docker ps
    root@ip-10-0-101-220:/home/ubuntu# docker ps
    CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS              PORTS                    NAMES
    9e10a00d6b47        local/locustexporter     "python /locust_ex..."   23 seconds ago      Up 21 seconds       0.0.0.0:4455->4455/tcp   observer-load-test_locustexporter_1
    114aded15c69        grafana/grafana:latest   "/run.sh"                24 seconds ago      Up 23 seconds       0.0.0.0:3000->3000/tcp   grafana
    cbb40d3b47da        local/locustserver       "/start.sh"              24 seconds ago      Up 23 seconds       0.0.0.0:8089->8089/tcp   observer-load-test_locustserver_1
    edb304567d3b        prom/prometheus          "/run.sh"                24 seconds ago      Up 23 seconds       0.0.0.0:9090->9090/tcp   observer-load-test_prometheus_1

## Operating the load test

1. If this is deployed on AWS, you may need to open the firewall to allow all traffic from your IP or configure access to the required ports. Access ports required:

```
grafana:3000
prometheus:9090
locust:8089
```

2. Access promtheus in order to verify all targets are configured and being scraped.

![Promtheus targets](images/targets.png?raw=true "Prometheus targets")

3. Access grafana in order to ensure that it is available and that everything has been loaded properly (default password: admin:secret)

![Prometheus dashboard](images/grafana.png?raw=true "Prometheus Grafana")

![Locust dashboard](images/locust.png?raw=true "Locust")

2. Access locust and set the value's that you need in order to begin the load test. In order to get a deeper understanding of locust please review the docs [here](https://docs.locust.io/en/stable/quickstart.html)

### At this stage the load test should be underway. You can use Grafana in order to observe the system under test.
