import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class TrafficLogbookStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const table = new dynamodb.Table(this, 'DynamoDBTable', {
      partitionKey: {name:'CustomerID', type: dynamodb.AttributeType.STRING},
      sortKey: {name:'ConnectionID', type: dynamodb.AttributeType.STRING},
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    table.addGlobalSecondaryIndex({
      indexName: 'ConnectionStateAndDate',
      partitionKey: {name: 'CustomerID', type: dynamodb.AttributeType.STRING},
      sortKey: {name: 'Status#CloseTime', type: dynamodb.AttributeType.STRING},
      projectionType: dynamodb.ProjectionType.ALL,
    })

    const lambdaGetStoppedConnections = new lambda.Function(this, 'lambdaGetStoppedConnections', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'get-stopped-connections.handler',
      code: lambda.Code.fromAsset('code'),
      timeout: cdk.Duration.minutes(1),
      environment: {
        TableName: table.tableName,
      },
    });
  
    const lambdaCreateConnection = new lambda.Function(this, 'lambdaCreateConnection', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'create-connection.handler',
      code: lambda.Code.fromAsset('code'),
      timeout: cdk.Duration.minutes(1),
      environment: {
        TableName: table.tableName,
      },
    });

    const lambdaCloseConnection = new lambda.Function(this, 'lambdaCloseConnection', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'close-connection.handler',
      code: lambda.Code.fromAsset('code'),
      timeout: cdk.Duration.minutes(1),
      environment: {
        TableName: table.tableName,
      },
    });

    const api = new apigateway.RestApi(this, 'api', {
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      }
    });
    // api.root.addCorsPreflight({
    //   allowOrigins: ['*'],
    //   allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    //   allowHeaders: ['Content-Type', 'Authorization', 'X-Amz-Date', 'X-Api-Key', 'X-Amz-Security-Token', 'X-Amz-User-Agent'],
    //   allowCredentials: true,
    // })
    const connections = api.root.addResource('connections').addMethod('GET', new apigateway.LambdaIntegration(lambdaGetStoppedConnections));
    const createConnection = api.root.addResource('connection')
    createConnection.addMethod('POST', new apigateway.LambdaIntegration(lambdaCreateConnection));
    const closeConnection = createConnection.addResource('{connection_id}').addMethod('PUT', new apigateway.LambdaIntegration(lambdaCloseConnection));

    table.grantFullAccess(lambdaGetStoppedConnections);
    table.grantFullAccess(lambdaCreateConnection);
    table.grantFullAccess(lambdaCloseConnection);
  }
}
