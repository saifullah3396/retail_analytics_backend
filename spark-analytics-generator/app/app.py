import sys

import pymongo
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, concat, from_json, lit

from schema import DEEPSTREAM_MSG_SCHEMA, TIMESTAMP_FORMAT


def foreach_batch_function(df, epoch_id):
    df.write.format("mongo").mode("append").save()
    # row.withColumn(  # generate a topic name with respect to each
    #     "topic",
    #     concat(
    #         lit("block-event-raw-org"),
    #         col("organization.id"),
    #         lit("-out"),
    #         col("outlet.id"),
    #         lit("-loc"),
    #         col("location.id"),
    #         lit("-f"),
    #         col("location.floor"),
    #         lit("-b"),
    #         col("location.block")))
    # pass

    def close(self, error):
        # Close the connection. This method in optional in Python.
        pass


spark = SparkSession \
    .builder \
    .appName("DSRetailytics-MongoDB-Connector") \
    .config(
        "spark.mongodb.input.uri",
        "mongodb://127.0.0.1:27017/retail_realtime_db") \
    .config(
        "spark.mongodb.output.uri",
        "mongodb://127.0.0.1:27017/retail_realtime_db") \
    .config(
        "spark.mongodb.output.collection",
        "events") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# # get input message stream from deepstream kafka topic
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "127.0.0.1:9092") \
    .option("subscribe", "block-event-raw-{}".format(sys.argv[1])) \
    .load() \

# # generate new kafka topic for the specific block
json_options = {
    "timestampFormat": TIMESTAMP_FORMAT
}

df = df \
    .selectExpr("cast(key as string)", "cast(value as string)") \
    .select(
        from_json("value", DEEPSTREAM_MSG_SCHEMA, json_options).alias("tmp")) \
    .select("tmp.*") \
    .writeStream \
    .foreachBatch(foreach_batch_function) \
    .start() \
    .awaitTermination()
