# # emoji_aggregator.py
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import from_json, col, window, when, to_json, struct
# from pyspark.sql.types import StructType, StructField, StringType, TimestampType

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

# # aggregated_df = aggregated_df.withColumn(
# #     "final_count",
# #     when(col("count") <= 1000, 1).otherwise(col("count") / 1000)
# # )
# aggregated_df = aggregated_df.withColumn(
#     "final_count",
#     when(col("count") <= 1000, col("count").cast("IntegerType")).otherwise((col("count") / 1000).cast("IntegerType"))
# )
# # Prepare data to send to Kafka
# output_df = aggregated_df.selectExpr(
#     "to_json(struct(*)) AS value"
# )

# query = output_df \
#     .writeStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "localhost:9092") \
#     .option("topic", "emoji_topic_aggregated") \
#     .option("checkpointLocation", "/tmp/spark_checkpoint") \
#     .start()

# query.awaitTermination()

# emoji_aggregator.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, when, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType  # Added IntegerType

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
    when(col("count") < 100, 
        col("count").cast(IntegerType())).otherwise((col("count") / 100).cast(IntegerType()))
)

# aggregated_df = aggregated_df.withColumn(
#     "final_count",
#     when(col("count") <= 100, 0)
#     .otherwise((col("count") / 100).cast(IntegerType()))
# )

# Prepare data to send to Kafka
output_df = aggregated_df.selectExpr(
    "to_json(struct(*)) AS value"
)

query = output_df \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "emoji_topic_aggregated") \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .start()

query.awaitTermination()