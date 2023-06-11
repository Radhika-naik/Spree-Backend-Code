import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Read the request body
    req_body = req.get_json()

    # Get the input values from the request body
    customer_phno = req_body.get('customer_phno')
    date_range = req_body.get('date_range')
    category = req_body.get('category')

    if not customer_phno or not date_range:
        return func.HttpResponse(
            "Please provide customer_phno and date_range.",
            status_code=400
        )

    # Connect to the Cosmos DB
    cosmosdb_uri = os.environ['CosmosDBURI']
    cosmosdb_key = os.environ['CosmosDBKey']
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'your_database_name'

    # Retrieve the receipts based on the provided inputs
    database = cosmos_client.get_database_client(database_name)

    # Retrieve the seller details for the given customer_phno
    seller_details = get_seller_details(database, customer_phno)

    # Retrieve the customer details for the given customer_phno
    customer_details = get_customer_details(database, customer_phno)

    # Retrieve the receipts for the given date_range and category
    receipt_details = get_receipt_details(database, date_range, category)

    return func.HttpResponse(f"Seller details: {seller_details}\n\nCustomer details: {customer_details}\n\nReceipts: {receipt_details}", status_code=200)

def get_seller_details(database, customer_phno):
    container_name = 'seller_details'

    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.seller_phno = '{customer_phno}'"
    result = container.query_items(query=query, enable_cross_partition_query=True)

    seller_details = list(result)

    return seller_details

def get_customer_details(database, customer_phno):
    container_name = 'customer_details'

    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.customer_phno = '{customer_phno}'"
    result = container.query_items(query=query, enable_cross_partition_query=True)

    customer_details = list(result)

    return customer_details

def get_receipt_details(database, date_range, category):
    container_name = 'receipt_details'

    container = database.get_container_client(container_name)
    query = f"SELECT * FROM c WHERE c.date_of_purchase BETWEEN '{date_range['start']}' AND '{date_range['end']}'"
    
    if category:
        query += f" AND c.category = '{category}'"

    result = container.query_items(query=query, enable_cross_partition_query=True)

    receipt_details = list(result)

    return receipt_details
