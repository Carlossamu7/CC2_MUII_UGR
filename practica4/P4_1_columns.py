#####################################
#                                   #
#      CLOUD COMPUTING - P4         #
#           1 - Columns             #
#   Carlos Santiago Sanchez Muñoz   #
#                                   #
#####################################

# Librerías
import sys
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql.functions import desc, row_number, monotonically_increasing_id
from pyspark.sql.window import Window

# Main
if __name__ == "__main__":
    conf = SparkConf().setAppName("Cloud Computing P4 - Columns")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)

    # Las columnas a extraer son la clase y las 6 mías
    cols_selected = ["class", "PSSM_r2_2_W", "PredCN_freq_central_2", "PSSM_r2_2_R", "PSSM_r1_4_A", "PSSM_r1_-4_Q", "PredCN_r2_1"]

    # Leyendo la cabecera
    df_header = sqlContext.read.csv("/user/datasets/ecbdl14/ECBDL14_IR2.header", header=False, sep=",", inferSchema=False)

    # Indicamos el número de columnas
    df_header = df_header.withColumn('row_num', row_number().over(Window.orderBy(monotonically_increasing_id())) - 2)
    df_header.show()

    # Permitimos consultas sql en el dataframe
    df_header.createOrReplaceTempView("sql_header")
    cols_names = ""

    # Guardamos el número de cada columna precedido de "_c"
    for it, col in enumerate(cols_selected):
        sql_row_num = sqlContext.sql("SELECT row_num FROM sql_header where _c0 like '@attribute "+ col +"%'").collect()[0]["row_num"]
        if it != 0:
            cols_names += ", _c" + str(sql_row_num)
        else:
            cols_names += "_c" + str(sql_row_num)

    # Mostramos los nombres escogidos
    print(cols_names)

    ### Extraemos las columnas del fichero de datos y las guardamos en un solo fichero en hdfs.
    df = sqlContext.read.csv("/user/datasets/ecbdl14/ECBDL14_IR2.data", header=False, sep=",", inferSchema=False)
    df.createOrReplaceTempView("sql_dataset")
    sqlDF = sqlContext.sql("SELECT " + cols_names + " FROM sql_dataset")
    sqlDF.show()
    sqlDF.repartition(1).write.option("header", "true").csv("p4_columns")

    sc.stop()
