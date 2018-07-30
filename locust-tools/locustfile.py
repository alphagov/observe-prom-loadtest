from locust import HttpLocust, TaskSet, task
import datetime
import requests
import os
import random

def find_metrics(host, app_name):
    r = requests.get('{}/api/v1/series?match[]={{job="{}"}}'.format(host, app_name)).json()
    return r['data']

metrics = find_metrics('https://prom-1.dj-test.dev.gds-reliability.engineering/', 'prometheus')

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

def get_labels(metrics):
    labels = set()
    for i in metrics:
        labels |= set(i.keys())
    return labels

grouped_metrics = group_metrics_by_name(metrics)

def generate_queries(grouped_metrics):
    queries = []
    for labels in grouped_metrics.itervalues():
        #if label == '__name__':
        names = labels['__name__']

        other_labels = labels.keys()
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

def create_task(query):
    def callable(l):
        response = l.client.get(query)
    return callable

def generate_tasks():
    tasks = []
    with open("/tmp/outfile") as f:
        content = f.readlines()
    for q in content:
        tasks.append(create_task("api/v1/query_range?query={}&&start=2018-07-22T00:00:00.00Z&end=".format(q)+datetime.datetime.utcnow().strftime("%Y-%m-%d")+"T23:59:00.0Z&step=15m"))
    return tasks

class UserBehavior(TaskSet):
    tasks = generate_tasks()

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000

if __name__ == '__main__':
    queries = generate_queries(grouped_metrics)
    with open('/tmp/outfile', 'w') as out:
        for q in queries:
            out.write(q + "\n")
