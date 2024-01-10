import json
import boto3
import os
from datetime import datetime
import random

table_name = os.getenv("TableName")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def getUsageData():
   usage = [ "1024", "2048", "4096", "8192" ]
   return random.choice(usage)

def closeConnection(ConnectionID):
   current_date = datetime.now()
   timestamp = current_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
   usage = getUsageData()

   response = table.update_item(
      Key={
         "CustomerID": "001", "ConnectionID": ConnectionID
      },
      UpdateExpression="set ConnectionStatus = :s, Bytes = :b, ConnectionStopDate = :d, #sd = :sd",
      ExpressionAttributeNames={
         "#sd": "Status#CloseTime"
      },
      ExpressionAttributeValues={
         ":s": "Stopped",
         ":b": usage,
         ":d": timestamp,
         ":sd": "Stopped#" + timestamp
      }
   )
   
   return response

def handler(event, context):
   path = event['path']
   ConnectionID = path.rsplit('/', 1)[-1]
   print(event)
   response = closeConnection(ConnectionID)
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