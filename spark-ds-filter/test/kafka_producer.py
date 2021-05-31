"""
Generates a fake deepstream kafka messages stream for testing purposes
"""

import copy
from json import dumps

from kafka import KafkaProducer

# read json example config
example_camera_event = {}
with open("./example_multi.json") as json_f:
    example_camera_event = json.loads(json_f)

# generate example events for multiple cameras
camera_handlers = []
cam_1_event = updated = copy.deepcopy(example_camera_event)
cam_1_event["sensor"]["id"] = 1
cam_2_event = updated = copy.deepcopy(example_camera_event)
cam_2_event["sensor"]["id"] = 2
cam_events = [cam_1_event, cam_2_event]

for idx in range(2):
    camera_handlers.append({})

    # generate event
    event = updated = copy.deepcopy(example_camera_event)
    event["sensor"]["id"] = idx

    # generate producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: dumps(x).encode('utf-8'))

    # generate topic
    topic = 'deepstream-raw-172.0.0.{}'.format(idx)

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
        updated["objects"][0]["local_coordinates"]["x"] = \
            event["objects"][0]["local_coordinates"]["x"] + step
        updated["objects"][1]["local_coordinates"]["y"] = \
            event["objects"][1]["local_coordinates"]["y"] + step
        updated["objects"][2]["local_coordinates"]["x"] = \
            event["objects"][2]["local_coordinates"]["x"] + step
        updated["objects"][2]["local_coordinates"]["y"] = \
            event["objects"][2]["local_coordinates"]["y"] + step

        handler['producer'].send(handler['topic'], value=updated)
    if step > 5.0:
        step = 0.0
    step += 0.05
    sleep(0.1)
    id_count += 1
