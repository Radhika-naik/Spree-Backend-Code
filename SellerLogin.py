import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Read the request body
    req_body = req.get_json()

    # Get the input values from the request body
    shop_phone_number = req_body.get('shop_phone_number')
    seller_password = req_body.get('seller_password')

    if not shop_phone_number or not seller_password:
        return func.HttpResponse(
            "Please provide both the shop phone number and seller password.",
            status_code=400
        )

    # Connect to the Cosmos DB
    cosmosdb_uri = os.environ['CosmosDBURI']
    cosmosdb_key = os.environ['CosmosDBKey']
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'your_database_name'
    container_name = 'seller_details'

    # Check if the seller exists in Cosmos DB
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.shop_phone_number = '{shop_phone_number}' AND c.seller_password = '{seller_password}'"
    result = container.query_items(query=query, enable_cross_partition_query=True)

    if len(list(result)) > 0:
        return func.HttpResponse("Seller logged in successfully.", status_code=200)

    return func.HttpResponse("Invalid phone number or password.", status_code=401)
