Prometheus Load generator for GDS RE Observe
============================================================================

This is a python scripted composed using locust as the source of load generation. The tool queries a remote prometheus in order to generate a list of queries base on metrics and a time interval.

When the quries are generated it then reads the list from a file. The file containes quries. The quries are then passed in to a staic URL which perform a range query. These queries are then run on the againest the prometheus server.

## Deployment method (Assuming that you already have a to loadtest deployed stack)

### AWS

1. Set up a server in AWS

    a. Boot a machine with the appropriate resources

    b. Optional, If you want persistence then attach a disk to the machine. The disk should be formated according to your requirments

    c.  Enusre that docker is installed on the system including docker compose
        
        curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose

    d. Make sure that this repositry is cloned on to the machine

2. Bring up the enviroment

    a. Once logged into to the machine, navigate to the cloned project repositry

    b. Configure the service by editing the 'locustfile.py' by setting the prometheus URL to your prometheus URL server. Please also specificy the job you would like run as a second argument.

    ```
    metrics = find_metrics('https://prom-1.dj-test.dev.gds-reliability.engineering/','prometheus')
    ```

    This is the section you need to edit. You also need to edit the variable in the locust exporter file.

    ```
    ENV PROM_SERVER='https://prom-1.dj-test.dev.gds-reliability.engineering/'
    ```

    c. ### IF YOU NEED AUTH EDIT THE LOCUST FILE USING [THESE INSTRUCTIONS](http://docs.python-requests.org/en/master/user/authentication/#basic-authentication)

    d. build the initial containers with the following commands:
        

        docker build -t local/locustserver .
        cd locustexporter
        docker build -t local/locustexporter .


    e. Please also make sure that you configure prometheus to scrape the prometheus that is the system under test. This can be done by adding the target prometheus server to the scrape config defined here: 
    
        {project_root}/config/prometheus-config.yaml

    f. If all is well you can configure the enviroment. In order to do that we run a docker compose command that should bring everything up as expected. Run this command as root since we have seen some issues with it.

        sudo docker-compose -f compose-env.yaml

    g. All should of gone well. You can verify this by running the following command and receiving similar output.

        docker ps 
        root@ip-10-0-101-220:/home/ubuntu# docker ps
        CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS              PORTS                    NAMES
        9e10a00d6b47        local/locustexporter     "python /locust_ex..."   23 seconds ago      Up 21 seconds       0.0.0.0:4455->4455/tcp   observer-load-test_locustexporter_1
        114aded15c69        grafana/grafana:latest   "/run.sh"                24 seconds ago      Up 23 seconds       0.0.0.0:3000->3000/tcp   grafana
        cbb40d3b47da        local/locustserver       "/start.sh"              24 seconds ago      Up 23 seconds       0.0.0.0:8089->8089/tcp   observer-load-test_locustserver_1


## Operating the load test

### AWS

1. You have to either open the firewall to allow all traffic from your IP or configrue access to the required ports

    a. Access ports reuqired:

        grafana:3000
        prometheus:9090
        locust:8089

2. Access promtheus in order to verify all targets including locust.

![Promtheus targets](images/targets.png?raw=true "Prometheus targets")

3. Access grafana in order to determine that all grafana's are avalible and that they have been loaded properly (defautl password: admin:secret)

![Prometheus dashboard](images/grafana.png?raw=true "Prometheus Grafana")


![Locust dashboard](images/locust.png?raw=true "Locust")

2. Access locust and set the value's that you need in order to evaluate your service. The more users the better.

### At this stage the load test should be underway. You can use graphs and a number of other things in order to observe the current system unders test.
