#####################################
#                                   #
#      CLOUD COMPUTING - P4         #
#      2 - Preprocesamiento         #
#   Carlos Santiago Sánchez Muñoz   #
#                                   #
#####################################

# Librerías
import sys
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql.functions import col, explode, array, lit

# Main
if __name__ == "__main__":
    conf = SparkConf().setAppName("Cloud Computing P4 - Preprocessing")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)

    # Lectura de datos
    df = sqlContext.read.csv("/tmp/data/datos.csv", header=True, sep=",", inferSchema=False)

    # Ratio de desbalanceo
    major = df.filter(col("_c631") == 0)
    minor = df.filter(col("_c631") == 1)
    ratio = float(major.count()/minor.count())
    print("Ratio de desbalanceo: " + str(ratio))

    # Subsamplig de la clase mayoritaria, uno los conjuntos de datos y guardo el summary
    sub_major = major.sample(False, 1/ratio)
    df2 = sub_major.unionAll(minor)

    # Separo en train y tests al 20-80%
    splits = df2.randomSplit([0.2, 0.8])
    test = splits[0]
    train = splits[1]

    # Guardo los datasets
    train.repartition(1).write.option("header", "true").csv("/tmp/data/processed/train")
    test.repartition(1).write.option("header", "true").csv("/tmp/data/processed/test")

    sc.stop()
