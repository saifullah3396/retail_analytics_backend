import os
import uuid

from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import (array, col, explode, flatten, from_json,
                                   lit, struct)
from schema import DEEPSTREAM_MSG_SCHEMA, TIMESTAMP_FORMAT

CAMERA_ANALYTICS_COLLECTION = "ds_analytics_cameraanalytics"
FLOOR_ANALYTICS_COLLECTION = "ds_analytics_flooranalytics"


def encode_objects(objects):
    """
    Encodes the objects in the same manner as the deepstream minimal
    encoding format
    """

    encoded_objects = []
    for obj in objects:
        # add object info
        encoded_obj = \
            "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(
                obj.event.type,
                obj.id,
                obj.confidence,
                obj.bbox.tlx,
                obj.bbox.tly,
                obj.bbox.brx,
                obj.bbox.bry,
                obj.direction,
                obj.orientation,
                obj.type)

        # add additional analytics info
        encoded_obj += "|#"
        encoded_obj += "|{},{}".format(
            obj.local_coordinates.x, obj.local_coordinates.y)
        encoded_obj += "|{},{}".format(
            obj.world_coordinates.x, obj.world_coordinates.y)

        encoded_objects.append(encoded_obj)
    return encoded_objects


class ForeachWriter:
    def open(self, partition_id, epoch_id):
        mongo_db_url = os.environ['MONGO_DB_URL']
        mongo_db_database = os.environ['MONGO_DB_DATABASE']
        self.connection = MongoClient(
            "mongodb://{}/{}".format(mongo_db_url, mongo_db_database))
        self.db = self.connection['retail_analytics_db']
        self.camera_analytics = self.db[CAMERA_ANALYTICS_COLLECTION]
        self.floor_analytics = self.db[FLOOR_ANALYTICS_COLLECTION]
        return True

    def process(self, row):
        print('row', row)
        # update floor info
        self.floor_analytics.update(
            {'_id': uuid.UUID(row.location.floor)},
            {
                "$set": {
                    'location_id': uuid.UUID(row.location.id),
                    'level': row.location.level,
                    'world_coordinates':
                        row.location.world_coordinates.asDict(recursive=True)},
                "$push": {
                    "heatmap_datapoints": {
                        "coordinates": [datapoint.asDict(recursive=True) for datapoint in row.heatmap_datapoints],
                        "timestamp": row.timestamp
                    }
                }
            },
            upsert=True
        )

        # update camera info
        objs = [obj.asDict(recursive=True) for obj in row.objects]
        self.camera_analytics.update(
            {'_id': uuid.UUID(row.sensor.id)},
            {
                "$set": {
                    'description': row.sensor.description,
                    'local_coordinates': row.sensor.local_coordinates.asDict(recursive=True),
                    'analyticsModule': row.analyticsModule.asDict(recursive=True),
                    'ds_analytics_flooranalytics_id': uuid.UUID(row.location.floor),
                },
                "$push": {
                    "events": {
                        "frame_id": row.id,
                        "version": row.version,
                        "timestamp": row.timestamp,
                        "objects": objs
                    }
                }
            },
            upsert=True
        )

    def close(self, error):
        pass


def main():
    """
    Entry point of this job
    """
    # get mongodb connection parameters
    kafka_broker_ip = os.environ['KAFKA_BROKER_IP']
    floor_topic = os.environ['FLOOR_TOPIC']

    # generate a new spark session
    spark = SparkSession \
        .builder \
        .appName("DSRetailytics-MongoDB-Connector") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # get input message stream from deepstream kafka topic
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker_ip) \
        .option("subscribe", floor_topic) \
        .load()

    # generate new kafka topic for the specific block
    json_options = {
        "timestampFormat": TIMESTAMP_FORMAT
    }

    # convert json to deepstream msg schema
    df = df \
        .selectExpr("cast(key as string)", "cast(value as string)") \
        .select(
            from_json(
                "value", DEEPSTREAM_MSG_SCHEMA, json_options).alias("tmp")) \
        .select("tmp.*")

    # generate data for heatmap
    df = df \
        .withColumn(  # add heatmap data coordinates x
            "heatmap_datapoints",
            F.expr("transform(objects, x -> x.world_coordinates)"))

    # write data to output
    df = df \
        .writeStream \
        .foreach(ForeachWriter()) \
        .start() \
        .awaitTermination()


if __name__ == "__main__":
    main()
