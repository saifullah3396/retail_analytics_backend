# Spark DSFilter application docker
This spark application performs one single job of filtering out deepstream
kafka streams into floor based streams.

# Build Docker
Build the docker image:
```
docker build --rm -t irl-ncai-retailytics/spark-analytics-generator .
```

# Run the application
```docker run --name app.py -e ENABLE_INIT_DAEMON=false --link spark-master:spark-master --net dockerspark_default -d bde/spark-app```