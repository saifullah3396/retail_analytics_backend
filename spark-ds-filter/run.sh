source ./env.sh
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 ./app/app.py