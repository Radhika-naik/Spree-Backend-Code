import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient
import uuid
from datetime import datetime
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Read the request body
    req_body = req.get_json()

    # Get the input values from the request body
    seller_receipt_no = req_body.get('seller_receipt_no')
    seller_phno = req_body.get('seller_phno')
    customer_phno = req_body.get('customer_phno')
    items = req_body.get('items')

    if not seller_receipt_no or not seller_phno or not customer_phno or not items:
        return func.HttpResponse(
            json.dumps({"code": "ERROR", "message": "Please provide seller_receipt_no, seller_phno, customer_phno, and items."}), 
            status_code=400,
            mimetype='application/json'
            )

    # Connect to the Cosmos DB
    cosmosdb_uri = 'URI'
    cosmosdb_key = 'key'
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'spreeDB'
    container_name = 'receipt_details'

    # Create unique entries for each item in the receipt
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    for item in items:
        item_name = item.get('item_name')
        quantity = item.get('quantity')
        total_price = item.get('total_price')
        date_of_purchase = item.get('date_of_purchase')

        if not item_name or not quantity or not total_price or not date_of_purchase:
            return func.HttpResponse(
                json.dumps({"code": "ERROR", "message": "Please provide all the required input parameters for each item."}),
                status_code=400,
                mimetype='application/json'
                )

        # Create a new entry for the item in the receipt
        receipt_id = generate_unique_receipt_id()
        receipt_details = {
            'id': str(uuid.uuid4()),
            'receipt_id': receipt_id,
            'seller_receipt_no': seller_receipt_no,
            'seller_phno': seller_phno,
            'customer_phno': customer_phno,
            'item_name': item_name,
            'quantity': quantity,
            'total_price': total_price,
            'date_of_purchase': date_of_purchase
        }
        container.create_item(body=receipt_details)

    return func.HttpResponse(
        json.dumps({"code": "SUCCESS", "message": "Receipt details stored successfully."}),
        status_code=200,
        mimetype='application/json'
        )

def generate_unique_receipt_id():
    # Generate a unique receipt ID using a combination of timestamp and a unique identifier
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4().hex)[:6]  # Generate a unique 6-character identifier
    receipt_id = f"{timestamp}_{unique_id}"
    return receipt_id
