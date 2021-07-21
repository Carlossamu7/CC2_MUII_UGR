#####################################
#                                   #
#      CLOUD COMPUTING - P4         #
#      3 - Machine Learning         #
#   Carlos Santiago Sánchez Muñoz   #
#                                   #
#####################################

# Librerías
import sys
import matplotlib.pyplot as plt
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql import Row
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression, NaiveBayes, LinearSVC
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

# Main
if __name__ == "__main__":
    conf = SparkConf().setAppName("Cloud Computing P4 - Machine Learning")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    sqlContext = SQLContext(sc)

    # Leemos los datos de entrenamiento y test
    train = sqlContext.read.csv("/tmp/data/train.csv",header=True,sep=",",inferSchema=True)
    test = sqlContext.read.csv("/tmp/data/test.csv",header=True,sep=",",inferSchema=True)

    # Cambiando formato para MLLib: nombre de la columna objetivo a 'label' y características en una columna de arrays
    train = train.withColumnRenamed("_c631", "label")
    assembler = VectorAssembler(
        inputCols=['_c488', '_c26', '_c472', '_c331', '_c176', '_c71'],
        outputCol='features'
    )
    train = assembler.transform(train)

    test = test.withColumnRenamed("_c631","label")
    assembler = VectorAssembler(
        inputCols=['_c488', '_c26', '_c472', '_c331', '_c176', '_c71'],
        outputCol='features'
    )
    test = assembler.transform(test)

    # Añadimos una columna con las caracteristicas escaladas entre 0 y 1
    scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")
    scalerModelTrain = scaler.fit(train)
    train = scalerModelTrain.transform(train)
    scalerModelTest = scaler.fit(test)
    test = scalerModelTrain.transform(test)

    # Archivo donde guardar todos los valores de accuracy
    f = open("/tmp/data/Accuracy.txt", "w+")

    #######################
    # Regresion Logistica #
    #######################

    # Regresión Logística 1 #
    lr = LogisticRegression(maxIter=10, regParam=0.2, elasticNetParam=0.7, family="binomial")
    lrModel_1 = lr.fit(train)
    predictions = lrModel_1.transform(test)
    # Accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    f.write("Accuracy RL1 (test): " + str(evaluator.evaluate(predictions)) + "\n")

    # Regresión Logística 2 #
    lr2 = LogisticRegression(maxIter=20, regParam=0.25, elasticNetParam=0.8, family="binomial")
    lrModel_2 = lr2.fit(train)
    predictions = lrModel_2.transform(test)
    # Accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    f.write("Accuracy RL2 (test): " + str(evaluator.evaluate(predictions)) + "\n")

    ###############
    # Naive Bayes #
    ###############

    # Naive Bayes 1 #
    nb = NaiveBayes(smoothing=2.0, featuresCol="scaled_features", labelCol="label", modelType="multinomial")
    nbModel_1 = nb.fit(train)
    predictions = nbModel_1.transform(test)
    # Accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    f.write("Accuracy NB1 (test): " + str(evaluator.evaluate(predictions)) + "\n")

    # Naive Bayes 2 #
    nb2 = NaiveBayes(smoothing=4.0, featuresCol="scaled_features", labelCol="label", modelType="multinomial")
    nbModel_2 = nb2.fit(train)
    predictions = nbModel_2.transform(test)
    # Accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    f.write("Accuracy NB2 (test): " + str(evaluator.evaluate(predictions)) + "\n")

    ##########################
    # Support Vector Machine #
    ##########################

    # Support Vector Machine  1 #
    lsvc = LinearSVC(maxIter=10, regParam=0.05)
    lsvcModel_1 = lsvc.fit(train)
    predictions = lsvcModel_1.transform(test)
    # Accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    f.write("Accuracy SVM1 (test): " + str(evaluator.evaluate(predictions)) + "\n")

    # Support Vector Machine  2 #
    lsvc = LinearSVC(maxIter=20, regParam=0.04)
    lsvcModel_2 = lsvc.fit(train)
    predictions = lsvcModel_2.transform(test)
    # Accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    f.write("Accuracy SVM2 (test): " + str(evaluator.evaluate(predictions)) + "\n")

    f.close()
