import json
import boto3
import os
from boto3.dynamodb.conditions import Key

table_name = os.getenv("TableName")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def getStoppedConnections():
   response = table.query(
      IndexName='ConnectionStateAndDate',
      KeyConditionExpression=(
         Key('CustomerID').eq("001")
         #& Key('Status#CloseTime').between("Stopped#2024-01-04T09:00:40.587255", "Stopped#2024-01-31T10:00:40.587255")
         & Key('Status#CloseTime').between("Stopped#2024-01-04T09:00:40.587255", "Stopped#2024-01-31T10:00:40.587255")
      )
   )
   
   return response['Items']

def handler(event, context):
   data = getStoppedConnections()

   return {
      'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            #"Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
      'statusCode': 200,
      'body': json.dumps(data)
   }