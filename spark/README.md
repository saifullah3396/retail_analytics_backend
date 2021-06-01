# Spark DSFilter application docker
This spark application performs one single job of filtering out deepstream
kafka streams into floor based streams.

# Running standalone applications
Run ds_filter.py application
```
./scripts/run_ds_filter.sh
```

Run run_analytics_generator.py application
```
./scripts/run_run_analytics_generator.sh
```

# Build Docker
Build the docker image for the images:
```
docker build --rm -t irl-ncai-retailytics/spark .
```

For running the spark applications in docker container, see ../docker/docker-compose-spark.yaml