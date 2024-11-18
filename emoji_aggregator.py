# # emoji_aggregator.py
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import from_json, col, window, when
# from pyspark.sql.types import StructType, StructField, StringType, TimestampType
# from pyspark.sql.streaming import DataStreamWriter

# spark = SparkSession \
#     .builder \
#     .appName("EmojiAggregator") \
#     .getOrCreate()

# schema = StructType([
#     StructField("user_id", StringType()),
#     StructField("emoji_type", StringType()),
#     StructField("timestamp", TimestampType())
# ])

# df = spark \
#     .readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "localhost:9092") \
#     .option("subscribe", "emoji_topic") \
#     .load() \
#     .selectExpr("CAST(value AS STRING) as json_str")

# json_df = df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

# aggregated_df = json_df \
#     .withWatermark("timestamp", "2 seconds") \
#     .groupBy(
#         window(col("timestamp"), "2 seconds"),
#         col("emoji_type")
#     ) \
#     .count()

# aggregated_df = aggregated_df.withColumn(
#     "final_count",
#     when(col("count") <= 1000, 1).otherwise(col("count") / 1000)
# )

# query = aggregated_df \
#     .select("window.start", "window.end", "emoji_type", "final_count") \
#     .writeStream \
#     .outputMode("update") \
#     .format("console") \
#     .option("truncate", "false") \
#     .start()

# query.awaitTermination()

# emoji_aggregator.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, when, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

spark = SparkSession \
    .builder \
    .appName("EmojiAggregator") \
    .getOrCreate()

schema = StructType([
    StructField("user_id", StringType()),
    StructField("emoji_type", StringType()),
    StructField("timestamp", TimestampType())
])

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "emoji_topic") \
    .load() \
    .selectExpr("CAST(value AS STRING) as json_str")

json_df = df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

aggregated_df = json_df \
    .withWatermark("timestamp", "2 seconds") \
    .groupBy(
        window(col("timestamp"), "2 seconds"),
        col("emoji_type")
    ) \
    .count()

aggregated_df = aggregated_df.withColumn(
    "final_count",
    when(col("count") <= 1000, 1).otherwise(col("count") / 1000)
)

# Select the relevant fields and serialize to JSON
output_df = aggregated_df.select(
    to_json(struct(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        "emoji_type",
        "final_count"
    )).alias("value")
)

# Write the output to Kafka topic 'emoji_topic_aggregated'
query = output_df \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "emoji_topic_aggregated") \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .start()

query.awaitTermination()