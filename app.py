from fastapi import FastAPI
from mangum import Mangum
import boto3
import os

app = FastAPI()
handler = Mangum(app)
rds_client = boto3.client('rds-data', region_name = 'us-west-1')

def execute(sql, type, args = []):
    response = rds_client.execute_statement(
        secretArn = os.environ.get('db_credentials_secrets_store_arn'),
        database = os.environ.get('database_name'),
        resourceArn = os.environ.get('db_cluster_arn'),
        sql = sql,
        parameters = args
    )
    
    if type in ['POST', 'UPDATE', 'DELETE']:
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {'status': 'success'}  
        else:
            return {'status': 'error', 'message': 'could modify into database'}

    elif type == 'GET':
        return response['records']

    return {'status': 'error', 'message': 'invalid type'}

@app.get('/')
async def root():
    return {'message': execute('SELECT * FROM users', 'GET')}