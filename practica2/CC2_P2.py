from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import logging
import pandas
import pymongo

# Arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['carlossamu7@correo.ugr.es'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
}

# DAG
dag = DAG(
    dag_id='CC_Practica2',
    default_args = default_args,
    description = 'Practica 2 de Cloud Computing',
    dagrun_timeout=timedelta(minutes=60),
    schedule_interval=timedelta(days=1),
)

# Make temporal directory
MakeDir = BashOperator(
    task_id='MakeDir',
    depends_on_past=False,
    bash_command='mkdir -p /tmp/practica2/',
    dag=dag
)

# Download temperature.csv
DownloadTemperature = BashOperator(
    task_id='DownloadTemperature',
    depends_on_past=False,
    bash_command='curl -o /tmp/practica2/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
    dag=dag
)

# Download humitidy.csv
DownloadHumidity = BashOperator(
    task_id='DownloadHumidity',
    depends_on_past=False,
    bash_command='curl -o /tmp/practica2/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
    dag=dag
)

#--------------------------------------------------------------------------------------------

# Unzip CSV
Unzip = BashOperator(
    task_id='Unzip',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/ && unzip /tmp/practica2/humidity.csv.zip && unzip /tmp/practica2/temperature.csv.zip',
    dag=dag
)

# Preprocess data
def preprocess():
    tem_csv = pandas.read_csv('/tmp/practica2/temperature.csv')
    hum_csv = pandas.read_csv('/tmp/practica2/humidity.csv')
    fecha = tem_csv['datetime']
    tem_san_francisco = tem_csv['San Francisco']
    hum_san_francisco = hum_csv['San Francisco']
    columnas = {'DATE': fecha,
                'TEMP': tem_san_francisco,
                'HUM': hum_san_francisco}
    datos = pandas.DataFrame(data=columnas)
    datos.fillna(datos.mean())
    datos.to_csv('/tmp/practica2/san_francisco.csv', encoding='utf-8', sep='\t', index=False)

Preprocessing = PythonOperator(
    task_id='preprocessing',
    python_callable=preprocess,
    op_kwargs={},
    dag=dag
)

# Storing in database -> Mongo
def store():
    datos = pandas.read_csv('/tmp/practica2/san_francisco.csv', sep='\t')
    datos = datos.to_dict('records')
    client = pymongo.MongoClient("mongodb+srv://1234:CC@cluster0.ff0rm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    code = client.CCAirflow['SanFrancisco'].insert_many(datos)

StoringData = PythonOperator(
    task_id='StoringData',
    python_callable=store,
    op_kwargs={},
    dag=dag
)

#--------------------------------------------------------------------------------------------

# Download APIs from GitHub
DownloadAPI1 = BashOperator(
    task_id='DownloadAPI1',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/ && rm -rf CC2_P2_API1 && git clone git@github.com:Carlossamu7/CC2_P2_API1.git',
    dag=dag
)


DownloadAPI2 = BashOperator(
    task_id='DownloadAPI2',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/ && rm -rf CC2_P2_API2 && git clone git@github.com:Carlossamu7/CC2_P2_API2.git',
    dag=dag
)

# Testing APIs
TestAPI1 = BashOperator(
    task_id='TestAPI1',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/CC2_P2_API1/ && pytest test.py',
    dag=dag
)

TestAPI2 = BashOperator(
    task_id='TestAPI2',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/CC2_P2_API2/ && pytest test.py',
    dag=dag
)

# Buildings dockers
BuildAPI1 = BashOperator(
    task_id='BuildAPI1',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/CC2_P2_API1/ && docker build --no-cache -t carlossamu7:CC2_P2_API1 -f Dockerfile .',
    dag=dag
)

BuildAPI2 = BashOperator(
    task_id='BuildAPI2',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/CC2_P2_API2/ && docker build --no-cache -t carlossamu7:CC2_P2_API2 -f Dockerfile .',
    dag=dag
)

# Deployments
DeployAPI1 = BashOperator(
    task_id='DeployAPI1',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/CC2_P2_API1/ && docker run -p 8000:8000 -d carlossamu7:CC2_P2_API1',
    dag=dag
)

DeployAPI2 = BashOperator(
    task_id='DeployAPI2',
    depends_on_past=False,
    bash_command='cd /tmp/practica2/CC2_P2_API2/ && docker run -p 8001:8001 -d carlossamu7:CC2_P2_API2',
    dag=dag
)

#--------------------------------------------------------------------------------------------
# Task DAGs
#--------------------------------------------------------------------------------------------

MakeDir >> DownloadTemperature >> DownloadHumidity >> Unzip
Unzip >> Preprocessing >> StoringData >> [DownloadAPI1, DownloadAPI2]
DownloadAPI1 >> TestAPI1 >> BuildAPI1 >> DeployAPI1
DownloadAPI2 >> TestAPI2 >> BuildAPI2 >> DeployAPI2
