import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Read the request body
    req_body = req.get_json()

    # Get the input values from the request body
    shop_phone_number = req_body.get('shop_phone_number')
    seller_password = req_body.get('seller_password')

    if not shop_phone_number or not seller_password:
        response = {
            "code": "ERROR",
            "message": "Please provide both the shop phone number and seller password."
            }
        return func.HttpResponse(
            json.dumps(response),
            status_code=400,
            mimetype='application/json'
            )

    # Connect to the Cosmos DB
    cosmosdb_uri = 'URI'
    cosmosdb_key = 'Key'
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'spreeDB'
    container_name = 'seller_details'

    # Check if the seller exists in Cosmos DB
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.shop_phone_number = '{shop_phone_number}' AND c.seller_password = '{seller_password}'"
    result = container.query_items(query=query, enable_cross_partition_query=True)

    if len(list(result)) > 0:
        response = {
            "code": "SUCCESS",
            "message": "Seller logged in successfully."
            }
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype='application/json'
            )

    return func.HttpResponse(
        json.dumps({"code": "ERROR", "message": "Invalid phone number or password."}),
        status_code=401,
        mimetype='application/json'
        )
