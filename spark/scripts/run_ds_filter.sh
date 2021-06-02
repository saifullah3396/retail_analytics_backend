SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source ${SCRIPTPATH}/env.sh
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 ${SCRIPTPATH}/../apps/ds_filter.py
