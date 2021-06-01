"""
Defines a spark job that reads a kafka stream from a deepstream server,
and separates the stream into multiple streams according to the floor id
"""

import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, concat, from_json, lit
from schema import DEEPSTREAM_MSG_SCHEMA, TIMESTAMP_FORMAT


def main():
    """
    Entry point of this job
    """

    # get topic of the deepstream server from conatiner environment variables
    kafka_broker_ip = os.environ['KAFKA_BROKER_IP']
    deepstream_server_topic = os.environ['DEEPSTREAM_SERVER_TOPIC']

    # generate spark context
    spark = SparkSession.builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # get input message stream from deepstream ka~fka topic
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker_ip) \
        .option(
            "subscribe",
            "{}".format(deepstream_server_topic)) \
        .load()

    # generate new kafka topic for the specific block
    json_options = {
        "timestampFormat": TIMESTAMP_FORMAT
    }

    df = df \
        .selectExpr("cast(key as string)", "cast(value as string)") \
        .select(
            from_json(
                "value",
                DEEPSTREAM_MSG_SCHEMA,
                json_options).alias("tmp")) \
        .select("tmp.*") \
        .withColumn(
            # generate a topic name with respect to each floor in location
            "topic",
            concat(lit("floor-raw-"), col("location.floor"))) \
        .selectExpr(
            'topic',
            'cast(id as string) as key',
            'to_json(struct(*)) as value') \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker_ip) \
        .option("checkpointLocation", "./checkpoint") \
        .start() \
        .awaitTermination()


if __name__ == "__main__":
    main()
