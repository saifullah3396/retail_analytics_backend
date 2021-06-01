"""
Generates a fake deepstream kafka messages stream for testing purposes
"""

import copy
import json
import uuid
from time import sleep

from kafka import KafkaProducer

# read json example config
cam_events = []
with open("./example.json") as json_f:
    cam_events = json.load(json_f)["cameras"]

# generate example events for multiple cameras
camera_handlers = []
for idx, event in enumerate(cam_events):
    camera_handlers.append({})

    # generate producer
    producer = KafkaProducer(
        bootstrap_servers=['127.0.0.1:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    # generate topic
    topic = 'deepstream-raw-fdf8f7523b6d'

    camera_handlers[idx]["event"] = event
    camera_handlers[idx]["producer"] = producer
    camera_handlers[idx]["topic"] = topic

step = 0.05
id_count = 0
while True:
    for handler in camera_handlers:
        event = handler['event']
        updated = copy.deepcopy(event)

        # change event id
        updated["id"] = id_count

        # generate data change
        # for idx, det_object in enumerate(updated["objects"]):
        #     updated["objects"][idx]["local_coordinates"]["x"] = \
        #         event["objects"][idx]["local_coordinates"]["x"] + step
        #     updated["objects"][idx]["local_coordinates"]["y"] = \
        #         event["objects"][idx]["local_coordinates"]["y"] + step

        handler['producer'].send(handler['topic'], value=updated)
    if step > 5.0:
        step = 0.0
    step += 0.05
    sleep(5)
    id_count += 1
