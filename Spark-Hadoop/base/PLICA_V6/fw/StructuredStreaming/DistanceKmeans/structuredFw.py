#!/usr/bin/env python
# bin/elasticsearch --elastic
#
# Run with: spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.4 structuredFw.py
# 

# Librerias

import findspark
findspark.init()

    # Procesamiento de datos

import sys
import math
import random 
import numpy as np
from datetime import datetime

import pyspark.sql.functions as F
from pyspark import SparkConf, SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *
from pyspark.ml import PipelineModel
from pyspark.ml.feature import StringIndexer, VectorAssembler, MinMaxScalerModel
from pyspark.ml.linalg import Vectors

    # Modelos de clustering 

from pyspark.ml.clustering import KMeansModel

# Variables

APP_NAME = "FW-SparkStreaming.py"
PREDICTION_TOPIC = sys.argv[2]
PERIOD = 10
BROKERS = sys.argv[1]
base_path = '/app/fw/StructuredStreaming/DistanceKMeans'
threshold = np.load(f'{base_path}/data/thresholdFw.npy',allow_pickle=True)
limit = 0

conf = SparkConf().setAppName(f"{APP_NAME}")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)
spark.conf.set("spark.sql.session.timeZone", "Europe/Madrid")
lines = spark.readStream.format("kafka").option("kafka.bootstrap.servers", BROKERS).option("subscribe", PREDICTION_TOPIC).option("failOnDataLoss", "false").load()

# Funciones 

    # Función de calculo del vector del centroid más cercano

def centroid (k,centers):
    return centers[k].tolist()

    # Función de calculo de distancia euclidea al centroid

def distToCentroid(datapt, centroid):
    return math.sqrt(Vectors.squared_distance(datapt, centroid))

    # Función para determinar anomalia

def anomalia (prediction, distance, threshold,limit):
    limit = min(limit,len(threshold[prediction]) - 1)
    if(round(distance,6) > round(threshold[prediction][limit],6)):
        return True
    return False

print('> Cargando estructura')

# Esquema

schema = StructType() \
    .add("version", StringType()) \
    .add("time", StringType()) \
    .add("id", StringType()) \
    .add("type", StringType()) \
    .add("event", StringType()) \
    .add("data",StructType() \
        .add('Time', StringType()) \
        .add('Blade', StringType()) \
        .add('Action', StringType()) \
        .add('Type', StringType()) \
        .add('Interface', StringType()) \
        .add('Origin', StringType()) \
        .add('Source', StringType()) \
        .add('Source User Name', StringType()) \
        .add('Destination', StringType()) \
        .add('Service', StringType()) \
        .add('Access Rule Number', StringType()) \
        .add('Access Rule Name', StringType()) \
        .add('Policy Name', StringType()) \
        .add('Description', StringType()) \
        .add('Id', StringType()) \
        .add('Marker', StringType()) \
        .add('Log Server Origin', StringType()) \
        .add('Interface Direction', StringType()) \
        .add('Interface Name', StringType()) \
        .add('Connection Direction', StringType()) \
        .add('Id Generated By Indexer', StringType()) \
        .add('First', StringType()) \
        .add('Sequencenum', StringType()) \
        .add('Source Zone', StringType()) \
        .add('Destination Zone', StringType()) \
        .add('Service ID', StringType()) \
        .add('Source Port', StringType()) \
        .add('Destination Port', StringType()) \
        .add('IP Protocol', StringType()) \
        .add('Xlate (NAT) Source IP', StringType()) \
        .add('Xlate (NAT) Source Port', StringType()) \
        .add('Xlate (NAT) Destination Port', StringType()) \
        .add('NAT Rule Number', StringType()) \
        .add('NAT Additional Rule Number', StringType()) \
        .add('Source Machine Name', StringType()) \
        .add('Hll Key', StringType()) \
        .add('Context Num', StringType()) \
        .add('Policy Management', StringType()) \
        .add('Db Tag', StringType()) \
        .add('Policy Date', StringType()) \
        .add('Product Family', StringType()) \
        .add('Logid', StringType()) \
        .add('Policy Rule UID', StringType()) \
        .add('Layer Name', StringType()) \
        .add('Needs Browse Time', StringType()) \
        .add('User', StringType()) \
        .add('Src User Dn', StringType()) \
        .add('Protocol', StringType()) \
        .add('Sig Id', StringType()) \
        .add('Reason', StringType()) \
        .add('Destination Machine Name', StringType()) \
        .add('Destination User Name', StringType()) \
        .add('Dst User Dn', StringType()) \
        .add('UserCheck ID', StringType()) \
        .add('Destination Object', StringType()) \
        .add('ICMP', StringType()) \
        .add('ICMP Type', StringType()) \
        .add('ICMP Code', StringType()) \
        .add('Client Name', StringType()) \
        .add('Product Version', StringType()) \
        .add('Domain Name', StringType()) \
        .add('Endpoint IP', StringType()) \
        .add('Authentication Status', StringType()) \
        .add('Identity Source', StringType()) \
        .add('Session ID', StringType()) \
        .add('Source Machine Group', StringType()) \
        .add('Authentication Method', StringType()) \
        .add('Identity Type', StringType()) \
        .add('Authentication Trial', StringType()) \
        .add('Source User Group', StringType()) \
        .add('Connection Id', StringType()) \
        .add('Last Update Time71', StringType()) \
        .add('Scheme', StringType()) \
        .add('Methods', StringType()) \
        .add('VPN Peer Gateway', StringType()) \
        .add('Community', StringType()) \
        .add('Mobile Access Session UID', StringType()) \
        .add('VPN Feature', StringType()) \
        .add('Duration', StringType()) \
        .add('Last Update Time79', StringType()) \
        .add('Update Count', StringType()) \
        .add('Creation Time', StringType()) \
        .add('Connections', StringType()) \
        .add('Aggregated Log Count', StringType()) \
        .add('_c84', StringType()))

dataset =  lines.select(F.from_json(F.col("value").cast("string"),schema).alias("dataset")).select("dataset.*")

# Preprocesamiento

dataset = dataset.select("version",F.col("time").alias('timestamp'),F.col("id").alias('id_sensor'),F.col("type").alias('type_sensor'),"event","data.Time","data.Blade","data.Action",\
                         "data.Type","data.Interface","data.Origin","data.Source","data.Source User Name","data.Destination",\
                         "data.Service","data.Access Rule Number","data.Access Rule Name","data.Policy Name","data.Description",\
                         "data.Id","data.Marker","data.Log Server Origin","data.Interface Direction","data.Interface Name",\
                         "data.Connection Direction","data.Id Generated By Indexer","data.First","data.Sequencenum","data.Source Zone",\
                         "data.Destination Zone","data.Service ID","data.Source Port","data.Destination Port","data.IP Protocol",\
                         "data.Xlate (NAT) Source IP","data.Xlate (NAT) Source Port","data.Xlate (NAT) Destination Port","data.NAT Rule Number",\
                         "data.NAT Additional Rule Number","data.Source Machine Name","data.Hll Key","data.Context Num","data.Policy Management",\
                         "data.Db Tag","data.Policy Date","data.Product Family","data.Logid","data.Policy Rule UID","data.Layer Name","data.Needs Browse Time",\
                         "data.User","data.Src User Dn","data.Protocol","data.Sig Id","data.Reason","data.Destination Machine Name","data.Destination User Name",\
                         "data.Dst User Dn","data.UserCheck ID","data.Destination Object","data.ICMP","data.ICMP Type","data.ICMP Code","data.Client Name",\
                         "data.Product Version","data.Domain Name","data.Endpoint IP","data.Authentication Status","data.Identity Source","data.Session ID",\
                         "data.Source Machine Group","data.Authentication Method","data.Identity Type","data.Authentication Trial","data.Source User Group",\
                         "data.Connection Id","data.Last Update Time71","data.Scheme","data.Methods","data.VPN Peer Gateway","data.Community","data.Mobile Access Session UID",\
                         "data.VPN Feature","data.Duration","data.Last Update Time79","data.Update Count","data.Creation Time","data.Connections","data.Aggregated Log Count","data._c84")

print('# Estructura cargada')
print('> Cargando modelos de preprocesamiento')

# Preprocesamiento

columns = dataset.columns[5:]
dataset = dataset.na.fill("N/A")

    # Cast string a tipos adecuados

dataset = dataset.withColumn("timestamp", F.from_unixtime(F.col("timestamp"), "yyyy-MM-dd'T'HH:mm:ssXXX"))
dataset = dataset.withColumn("time", F.to_timestamp(F.col("Time"), 'MM/dd/yyyy hh:mm:ss a'))
dataset = dataset.withColumn("time", F.date_format(F.col("Time"), "yyyy-MM-dd'T'HH:mm:ssXXX"))

dataset = dataset.withColumn('First', F.col('First').cast(BooleanType()))
dataset = dataset.withColumn('Sequencenum', F.col('Sequencenum').cast(IntegerType()))

    # Creamos col hora

dataset = dataset.withColumn("hour", F.hour(F.col("time")))

    # Normalizamos columna hora

dataset = dataset.withColumn("hour", (F.col("hour") - 0) / (23 - 0)*6)

    # Cambio formato a binario col First

dataset = dataset.withColumn('First_index', F.when(F.col('First') == True,1).otherwise(0))

    # OneHotEncoding

ohe_model_path = "{}/data/oheModel.bin".format(base_path)
ohe = PipelineModel.load(ohe_model_path)
dataset = ohe.transform(dataset)

    # StringIndexer

string_indexer_model_path = "{}/data/stringIndexerModel.bin".format(base_path)
string_indexer = PipelineModel.load(string_indexer_model_path)
dataset = string_indexer.transform(dataset)

    # MinMaxScaler

minMaxScaler_model_path = "{}/data/minMaxScalerModel.bin".format(base_path)
minMaxScaler = PipelineModel.load(minMaxScaler_model_path)
dataset = minMaxScaler.transform(dataset)
    
    # VectorAssembler

vector_assembler_output_path = "{}/data/vectorAssemblerModel.bin".format(base_path)
vector_assembler = VectorAssembler.load(vector_assembler_output_path)
dataset = vector_assembler.transform(dataset)

print('# Modelos de preprocesamiento cargados')
print('> Cargando KMeans')

# Clasificación

model_path = "{}/data/distanceKmeansFwModel.bin".format(base_path)
model = KMeansModel.load(model_path)
predictions = model.transform(dataset)

centers = model.clusterCenters()

vectorCent = F.udf(lambda k: centroid(k,centers), ArrayType(DoubleType()))
euclDistance = F.udf(lambda data,centroid: distToCentroid(data,centroid),FloatType())
detectAnom = F.udf(lambda prediction, distance: anomalia(prediction, distance, threshold, limit), BooleanType())

predictions  = predictions.withColumn('centroid', vectorCent(F.col('prediction')))
predictions = predictions.withColumn('distance', euclDistance(F.col('features'),F.col('centroid')))
predictions = predictions.withColumn('anomalia', detectAnom(F.col('prediction'),F.col('distance')))

print('# KMeans cargado ')

only_predictions = predictions.select('version','timestamp','id','type','event', *columns,'anomalia')

# Cambio de nombre a originales

predictions = predictions.withColumnRenamed('type_sensor','type' )
predictions = predictions.withColumnRenamed('id_sensor','id' )

# Comienzo
print('# Comienzo ')

#only_predictions.writeStream.outputMode("append").format("console").start().awaitTermination()
only_predictions.writeStream.outputMode("append").format("org.elasticsearch.spark.sql").option("checkpointLocation",'/tmp/checkpoint6').option("es.nodes",sys.argv[3]).option("es.port",sys.argv[4]).option("es.nodes.wan.only","true").option("es.net.http.auth.user",sys.argv[5]).option("es.net.http.auth.pass",sys.argv[6]).option("es.resource","firewall/doc-type").start("firewall/doc-type").awaitTermination()
