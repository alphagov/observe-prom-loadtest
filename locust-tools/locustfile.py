from locust import HttpLocust, TaskSet, task
import requests
import os
import random

def find_metrics(host, app_name):
    r = requests.get('{}/api/v1/series?match[]={{job="{}"}}'.format(host, app_name)).json()
    return r['data']

metrics = find_metrics('https://prom-1.dj-test.dev.gds-reliability.engineering/','prometheus')

def group_metrics_by_dimension(metrics):
    bucketed_metrics = {}
    for i in metrics:
        bucket = frozenset(i.keys())
        if not bucket in bucketed_metrics:
            bucketed_metrics[bucket] = {}

        for label in bucket:
            if label not in bucketed_metrics[bucket]:
                bucketed_metrics[bucket][label] = set()
            bucketed_metrics[bucket][label].add(i[label])

    return bucketed_metrics

def group_metrics_by_name(metrics):
    bucketed_metrics = {}
    for i in metrics:
        bucket = i['__name__']
        if not bucket in bucketed_metrics:
            bucketed_metrics[bucket] = {}

        for label in i.keys():
            if label not in bucketed_metrics[bucket]:
                bucketed_metrics[bucket][label] = set()
            bucketed_metrics[bucket][label].add(i[label])

    return bucketed_metrics

#start_time = datetime.now_utc()



def get_labels(metrics):
    labels = set()
    for i in metrics:
        labels |= set(i.keys())
    return labels

grouped_metrics = group_metrics_by_name(metrics)

#print grouped_metrics
def generate_queries(grouped_metrics):
    queries = []
    for labels in grouped_metrics.itervalues():
        #if label == '__name__':
        names = labels['__name__']

        other_labels = labels.keys() #get a list of the labels
        other_labels.remove('__name__')

        for name in names:
            random_label = {}
            for i in other_labels:
                print ("{}: {}, {}".format(name, i,list(labels[i])))
                value = random.choice(list(labels[i]))
                random_label[i] = value
            random_label = ', '.join(['{key}="{value}"'.format(key=k, value=v) for k, v in random_label.iteritems()])


            queries.append('{metric_name}{{{labels}}}'.format(
                metric_name=name,
                labels=random_label,
            ))
    return queries


# /query_range?query=up&start=2018-07-10T00:00:00.00Z&end=2018-07-20T0:00:00.0Z&step=15m

# ['%{}.%{}'.format(key, value) for key,value in attributes.iteritems].join(',')




def create_task(query):
    def callable(l):
        response = l.client.get(query)
        #print query
        #print("Response status code:", response.status_code)
    return callable

def generate_tasks():
    tasks = []
    with open("/tmp/outfile") as f:
        content = f.readlines()
    for q in content:
        tasks.append(create_task("/api/v1/query_range?query={}&&start=2018-07-22T00:00:00.00Z&end=2018-07-25T0:00:00.0Z&step=15m".format(q)))
    return tasks

class UserBehavior(TaskSet):
    tasks = generate_tasks()
#    @task(2)
#    def index(self):
#        response = self.client.get("/api/v1/query?query=up&start=2018-07-10T00:00:00.00Z&end=2018-07-20T0:00:00.0Z&step=15m")
#        print("Response content:", response.text)

#    def on_start(self):
#        with open("/tmp/outfile") as f:
#            content = f.readlines()
#        for q in content:
#            UserBehavior.tasks.append(create_task(self.client, "/api/v1/query_range?query={}&&start=2018-07-22T00:00:00.00Z&end=2018-07-24T0:00:00.0Z&step=15m".format(q)))
          #  metric_name{label="value", label2="value2"}
          #  http_requests{job="http-simulator", status="200"}

          # datetime.datetime.now().isoformat()


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000

if __name__ == '__main__':
    queries = generate_queries(grouped_metrics)
    with open('/tmp/outfile', 'w') as out:
        for q in queries:
            out.write(q + "\n")
