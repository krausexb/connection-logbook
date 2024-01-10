import json
import boto3
import os
from datetime import datetime
import uuid

table_name = os.getenv("TableName")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def createConnection():
   current_date = datetime.now()
   timestamp = current_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
   connection_uuid = str(uuid.uuid4())

   response = table.put_item(
      Item={
         "CustomerID": "001", "ConnectionID": connection_uuid, "Status#CloseTime": "Started#", "ConnectionStatus":"Started", "ConnectionStartDate": timestamp,
      }
   )
   
   return response

def handler(event, context):
   response = createConnection()
   return {
      'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            #"Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
      'statusCode': 200,
      'body': json.dumps(response)
   }