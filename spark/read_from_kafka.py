from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession  \
	.builder  \
	.config("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", False) \
	.appName("StructuredSocketRead")  \
	.getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

lines = spark  \
	.readStream  \
	.format("kafka")  \
	.option("kafka.bootstrap.servers","18.211.252.152:9092")  \
	.option("subscribe","real-time-project")  \
	.load()

kafkaDF = lines.selectExpr("cast(value as string)", "topic", "timestamp")

schema = StructType([
	StructField("invoice_no", LongType()),
	StructField("country", StringType()),
	StructField("timestamp", TimestampType()),
	StructField("type", StringType()),
	StructField("items", ArrayType(
		StructType([
			StructField("SKU", StringType()),
			StructField("title", StringType()),
			StructField("unit_price", FloatType()),
			StructField("quantity", IntegerType()),
		])
	))
])  	

# raw batch data 
rawKafkaData = kafkaDF.select(from_json(col('value'), schema).alias('data'), 'timestamp')

# create sales data with required cols from the raw kafka data
# also calulate total items and total cost for each invoice, and if its a order or a return
salesData = rawKafkaData.select('data.invoice_no', 'data.items', 'data.type', 'data.country', 'data.timestamp') \
	.withColumn('total_items', aggregate("items", lit(0), lambda acc, x: acc + x.quantity)) \
	.withColumn('total_cost', round(aggregate("items", lit(0.0), lambda acc, x: acc + x.quantity * x.unit_price), 2)) \
	.withColumn('is_order', when(col('type') == 'ORDER', 1).otherwise(0)) \
	.withColumn('is_return', when(col('type') == 'RETURN', 1).otherwise(0)) \
	.withColumn('total_cost', when(col('is_return') == 1, - col('total_cost')).otherwise(col('total_cost'))) \
	.drop("items", "type")

salesData.writeStream \
	.format("console") \
	.outputMode("append") \
	.option("truncate", "false") \
	.trigger(processingTime="1 minute") \
	.start()

# calculate data for time based KPI's
aggregateDataByTime = salesData.select('invoice_no', 'timestamp', 'total_items', 'total_cost', 'is_order', 'is_return') \
	.withWatermark("timestamp", "1 minute") \
	.groupBy(window(col("timestamp"), "1 minute", "1 minute")) \
	.agg(
		format_number(sum("total_cost"), 2).alias('total_sales_vol'),
		format_number(avg("total_cost"), 2).alias('avg_transaction_size'),
		count("invoice_no").alias("OPM"),
		format_number(avg("is_return"), 2).alias('rate_of_return')
	)

# calculate data for time and country based KPI's
aggregateDataByCountry = salesData.select('invoice_no', 'timestamp', 'country', 'total_items', 'total_cost', 'is_order', 'is_return') \
	.withWatermark("timestamp", "1 minute") \
	.groupBy(window(col("timestamp"), "1 minute", "1 minute"), "country") \
	.agg(
		format_number(sum("total_cost"), 2).alias('total_sales_vol'),
		format_number(avg("total_cost"), 2).alias('avg_transaction_size'),
		count("invoice_no").alias("OPM"),
		format_number(avg("is_return"), 2).alias('rate_of_return')
	)

aggregateDataByTime.writeStream \
	.format("json") \
	.outputMode("append") \
	.option("truncate", "false") \
	.trigger(processingTime="1 minute") \
	.option("path", "./time/") \
	.option("checkpointLocation", "./time-cp/") \
	.start()


aggregateDataByCountry.writeStream \
	.format("json") \
	.outputMode("append") \
	.option("truncate", "false") \
	.trigger(processingTime="1 minute") \
	.option("path", "./country/") \
	.option("checkpointLocation", "./country-cp/") \
	.start()

spark.streams.awaitAnyTermination()
