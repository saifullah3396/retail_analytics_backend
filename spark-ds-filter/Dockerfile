FROM bde2020/spark-python-template:3.1.1-hadoop3.2

ENV SPARK_KAFKA_PKG="org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2"
ENV SPARK_SUBMIT_ARGS="--packages ${SPARK_KAFKA_PKG}"
ENV SPARK_MASTER_NAME spark-master
ENV SPARK_MASTER_PORT 7077
ENV SPARK_APPLICATION_PYTHON_LOCATION /app/app.py

COPY ./app /app