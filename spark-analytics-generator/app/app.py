import os

import pymongo
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, explode, from_json, lit, struct
from schema import DEEPSTREAM_MSG_SCHEMA, TIMESTAMP_FORMAT

FLOORS_COLLLECTION = "floors"
HEATMAP_COORDINATES_COLLLECTION = "heatmap_coordinates"
CAMERAS_COLLLECTION = "cameras"
CAMERA_EVENTS_COLLLECTION = "camera_events"


def write_batch(df, epoch_id):
    cameras_df = df.select("{}.*".format(CAMERAS_COLLLECTION))
    cameras_df.write.format("mongo") \
        .mode("append") \
        .option("collection", CAMERAS_COLLLECTION) \
        .save()

    camera_events_df = df.select(
        "{}.*".format(CAMERA_EVENTS_COLLLECTION))
    camera_events_df.write.format("mongo") \
        .mode("append") \
        .option("collection", CAMERA_EVENTS_COLLLECTION) \
        .save()

    heatmap_coordinates_df = df.select(
        "{}.*".format(HEATMAP_COORDINATES_COLLLECTION))
    heatmap_coordinates_df.write.format("mongo") \
        .mode("append") \
        .option("collection", HEATMAP_COORDINATES_COLLLECTION) \
        .save()


def main():
    """
    Entry point of this job
    """
    # get mongodb connection parameters
    kafka_broker_ip = os.environ['KAFKA_BROKER_IP']
    mongo_db_url = os.environ['MONGO_DB_URL']
    mongo_db_database = os.environ['MONGO_DB_DATABASE']
    floor_topic = os.environ['FLOOR_TOPIC']

    # generate a new spark session
    spark = SparkSession \
        .builder \
        .appName("DSRetailytics-MongoDB-Connector") \
        .config(
            "spark.mongodb.input.uri",
            "mongodb://{}/{}".format(mongo_db_url, mongo_db_database)) \
        .config(
            "spark.mongodb.output.uri",
            "mongodb://{}/{}".format(mongo_db_url, mongo_db_database)) \
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
        .withColumn(  # add floor id column
            "_id", col("location.floor")) \
        .withColumn(  # add floor column with its data
            FLOORS_COLLLECTION,
            struct(
                col("_id"),
                col("location.id"),
                col("location.level"),
                col("location.world_coordinates"))) \
        .withColumn(
            # add floor_id column for referencing floors in other columns
            "{}_id".format(FLOORS_COLLLECTION),
            col("location.floor")) \
        .withColumn(  # add heatmap data coordinates
            "hm_coords_x",
            explode("objects.world_coordinates.x")) \
        .withColumn(  # add heatmap data coordinates
            "hm_coords_y",
            explode("objects.world_coordinates.y")) \
        .withColumn(  # add heatmap data coordinates
            HEATMAP_COORDINATES_COLLLECTION,
            struct(
                # add reference to camera collection
                col("{}_id".format(FLOORS_COLLLECTION)),
                col("hm_coords_x").alias('x'),
                col("hm_coords_y").alias('y')))

    # generate data for camera realtime events
    df = df \
        .withColumn(
            "_id", col("sensor.id")) \
        .withColumn(
            CAMERAS_COLLLECTION,
            struct(
                col("_id"),
                col("{}_id".format(FLOORS_COLLLECTION)),
                col("sensor.description"),
                col("sensor.local_coordinates"),
                col("analyticsModule"))) \
        .withColumn(
            "{}_id".format(CAMERAS_COLLLECTION), col("sensor.id")) \
        .withColumn(
            CAMERA_EVENTS_COLLLECTION,
            struct(
                col("id"),
                # add reference to camera collection
                col("{}_id".format(CAMERAS_COLLLECTION)),
                col("version"),
                col("@timestamp"),
                col("objects")))

    # write data to output
    df = df.select(
        CAMERAS_COLLLECTION,
        CAMERA_EVENTS_COLLLECTION,
        HEATMAP_COORDINATES_COLLLECTION) \
        .writeStream \
        .foreachBatch(write_batch) \
        .start() \
        .awaitTermination()


if __name__ == "__main__":
    main()
