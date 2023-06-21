import logging
import os
import azure.functions as func
import json
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for customer login.')

    # Read the request body
    req_body = req.get_json()

    # Get the input values from the request body
    customer_phno = req_body.get('customer_phno')
    customer_password = req_body.get('customer_password')

    if not customer_phno or not customer_password:
        return func.HttpResponse(
            json.dumps({"code": "ERROR", "message": "Please provide customer_phno and customer_password."}),
            status_code=400,
            mimetype='application/json'
            )

    # Connect to the Cosmos DB
    cosmosdb_uri = 'URI'
    cosmosdb_key = 'Key'
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'spreeDB'
    container_name = 'customer_details'

    # Check if the customer exists in Cosmos DB
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.customer_phno = '{customer_phno}' AND c.customer_password = '{customer_password}'"
    result = container.query_items(query=query, enable_cross_partition_query=True)

    if len(list(result)) > 0:
        return func.HttpResponse(
            json.dumps({"code": "SUCCESS", "message": "Customer logged in successfully."}),
            status_code=200,
            mimetype='application/json'
            )

    return func.HttpResponse(
        json.dumps({"code": "ERROR", "message": "Invalid phone number or password."}),
        status_code=401,
        mimetype='application/json'
        )
