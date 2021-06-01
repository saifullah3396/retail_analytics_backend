from pyspark.sql.types import (ArrayType, DoubleType, IntegerType, StringType,
                               StructType, TimestampType)

TIMESTAMP_FORMAT = "yyyy-MM-dd\'T\'HH:mm:ss.sss\'Z\'"

DEEPSTREAM_MSG_SCHEMA = StructType() \
    .add("version", StringType(), True) \
    .add("id", IntegerType(), True) \
    .add("@timestamp", TimestampType(), True) \
    .add(
        "location",
        StructType()
        .add("id", StringType(), True)
        .add("floor", StringType(), True)
        .add("level", StringType(), True)
        .add(
            "world_coordinates",
            StructType()
            .add("x", DoubleType(), True)
            .add("y", DoubleType(), True))) \
    .add(
        "sensor",
        StructType()
        .add("id", StringType(), True)
        .add("description", StringType(), True)
        .add(
            "local_coordinates",
            StructType()
            .add("x", DoubleType(), True)
            .add("y", DoubleType(), True))) \
    .add(
        "analyticsModule",
        StructType()
        .add("id", StringType(), True)
        .add("description", StringType(), True)
        .add("source", StringType(), True)
        .add("version", StringType(), True)) \
    .add("objects", ArrayType(StringType()))
