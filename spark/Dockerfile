FROM bitnami/spark:latest

ENV SPARK_PGS="org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2,\org.mongodb.spark:mongo-spark-connector_2.12:3.0.1"

# install spark-packages required
RUN curl \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.1.1/spark-sql-kafka-0-10_2.12-3.1.1.jar \
    --output /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.1.1.jar

RUN curl \
    https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/3.0.1/mongo-spark-connector_2.12-3.0.1.jar \
    --output /opt/bitnami/spark/jars/mongo-spark-connector_2.12-3.0.1.jar

COPY ./apps /opt/bitnami/spark/apps/