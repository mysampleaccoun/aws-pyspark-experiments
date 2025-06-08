from pyspark.sql import SparkSession
from pyspark.sql.functions import avg,desc,count,rank
from pyspark.sql.functions import year
from pyspark.sql.window import  Window

# Create SparkSession
spark = SparkSession.builder \
    .appName("PySpark Hands-On") \
    .getOrCreate()
# read data
df= spark.read.csv("s3://my-pyspark/employees.csv",header=True)
df=df.dropna()


new_df = df.withColumn("BONUS", df["SALARY"] * 0.10)
new_df=new_df.withColumn("TOTAL_COMPENSATION",new_df["SALARY"] + new_df["BONUS"])
new_df =new_df.withColumn("YEAR",year("HIRE_DATE"))
avg_salary = new_df.groupBy("DEPARTMENT_ID").agg(avg("SALARY").alias("Avg_salary"))
count = new_df.groupBy("DEPARTMENT_ID").agg(count("EMPLOYEE_ID"))
window_function= Window.partitionBy("DEPARTMENT_ID").orderBy("SALARY")
new_df =new_df.withColumn("RANK",rank().over(window_function))
new_df=new_df.withColumn("HIGHEST_SALARY",new_df["RANK"]==1)
new_df = new_df.orderBy(desc("TOTAL_COMPENSATION")).limit(10)

# Show data
new_df.write.mode("overwrite").option("header", True).csv("s3://my-pyspark/output/employee_summary")
avg_salary.write.mode("overwrite").option("header", True).csv("s3://my-pyspark/output/department_salary_avg")
count.write.mode("overwrite").option("header", True).csv("s3://my-pyspark/output/count")


# Stop Spark
spark.stop()
