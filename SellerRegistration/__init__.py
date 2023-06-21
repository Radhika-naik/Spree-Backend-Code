import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient
import uuid
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Read the request body
    req_body = req.get_json()

    # Get the input values from the request body
    shop_name = req_body.get('shop_name')
    shop_category = req_body.get('shop_category')
    shop_phone_number = req_body.get('shop_phone_number')
    shop_email = req_body.get('shop_email')
    shop_address = req_body.get('shop_address')
    shop_gst_number = req_body.get('shop_gst_number')
    seller_password = req_body.get('seller_password')

    if not shop_name or not shop_category or not shop_phone_number or not shop_email or not shop_address or not shop_gst_number or not seller_password:
        return func.HttpResponse(
            json.dumps({"code": "ERROR", "message": "Please provide all the required input parameters."}),
            status_code=400,
            mimetype='application/json'
            )

    # Connect to the Cosmos DB
    cosmosdb_uri = 'URI'
    cosmosdb_key = 'Key'
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'spreeDB'
    container_name = 'seller_details'

    # Check if the seller already exists in Cosmos DB
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.shop_phone_number = '{shop_phone_number}'"
    result = container.query_items(query=query, enable_cross_partition_query=True)

    if len(list(result)) > 0:
        return func.HttpResponse(
            json.dumps({"code": "SUCCESS", "message": "Seller already exists."}),
            status_code=200,
            mimetype='application/json'
            )

    # Create a new seller entry
    seller_details = {
        'id': str(uuid.uuid4()),
        'shop_name': shop_name,
        'shop_category': shop_category,
        'shop_phone_number': shop_phone_number,
        'shop_email': shop_email,
        'shop_address': shop_address,
        'shop_gst_number': shop_gst_number,
        'seller_password': seller_password
    }
    container.create_item(body=seller_details)

    return func.HttpResponse(
        json.dumps({"code": "SUCCESS", "message": "Seller registered."}),
        status_code=200,
        mimetype='application/json'
        )

