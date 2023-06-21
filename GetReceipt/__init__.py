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
    customer_phno = req_body.get('customer_phno')
    date_range = req_body.get('date_range')
    category = req_body.get('category')

    if not customer_phno or not date_range:
        return func.HttpResponse(
            json.dumps({"code": "ERROR", "message": "Please provide customer_phno and date_range."}),
            status_code=400,
            mimetype='application/json'
            )

    # Connect to the Cosmos DB
    cosmosdb_uri = 'URI'
    cosmosdb_key = 'Key'
    cosmos_client = CosmosClient(cosmosdb_uri, cosmosdb_key)
    database_name = 'spreeDB'

    # Retrieve the receipts based on the provided inputs
    database = cosmos_client.get_database_client(database_name)

    # Retrieve the receipts for the given date_range and category
    receipt_details = get_receipt_details(database, customer_phno, date_range, category)
    response = {
    "code": "SUCCESS",
    "message": {
        "receipt_details": receipt_details
    }
    }   

    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype='application/json'
        )

def get_receipt_details(database, customer_phno, date_range, category):
    container_name = 'receipt_details'
    seller_container_name = 'seller_details'

    container = database.get_container_client(container_name)
    seller_container = database.get_container_client(seller_container_name)

    query = f"SELECT r.seller_receipt_no, r.seller_phno, r.customer_phno, r.date_of_purchase, r.item_name, r.quantity, r.total_price FROM c as r WHERE r.customer_phno = '{customer_phno}' AND r.date_of_purchase >= '{date_range['start']}' AND r.date_of_purchase <= '{date_range['end']}'"


    result = container.query_items(query=query, enable_cross_partition_query=True)
    receipt_details = list(result)

    formatted_receipts = {}
    for receipt in receipt_details:
        seller_receipt_no = receipt['seller_receipt_no']
        if seller_receipt_no not in formatted_receipts:
            formatted_receipts[seller_receipt_no] = {
                'shop_name': None,
                'shop_category': None,
                'shop_phno': None,
                'shop_email': None,
                'shop_address': None,
                'shop_gst_number': None,
                'seller_password': None,
                'items_details': []
            }

        formatted_receipts[seller_receipt_no]['items_details'].append({
            'item_name': receipt['item_name'],
            'quantity': receipt['quantity'],
            'total_price': receipt['total_price'],
            'date_of_purchase': receipt['date_of_purchase']
        })

        if not formatted_receipts[seller_receipt_no]['shop_phno']:
            shop_phno = receipt['seller_phno']
            seller_query = f"SELECT * FROM c WHERE c.shop_phone_number = '{shop_phno}'"
            seller_result = seller_container.query_items(query=seller_query, enable_cross_partition_query=True)
            seller_details = list(seller_result)

            if seller_details:
                formatted_receipts[seller_receipt_no]['shop_name'] = seller_details[0]['shop_name']
                formatted_receipts[seller_receipt_no]['shop_category'] = seller_details[0]['shop_category']
                formatted_receipts[seller_receipt_no]['shop_phno'] = seller_details[0]['shop_phone_number']
                formatted_receipts[seller_receipt_no]['shop_email'] = seller_details[0]['shop_email']
                formatted_receipts[seller_receipt_no]['shop_address'] = seller_details[0]['shop_address']
                formatted_receipts[seller_receipt_no]['shop_gst_number'] = seller_details[0]['shop_gst_number']
                formatted_receipts[seller_receipt_no]['seller_password'] = seller_details[0]['seller_password']

    formatted_receipts = list(formatted_receipts.values())

    if category:
        formatted_receipts = [receipt for receipt in formatted_receipts if receipt['shop_category'] == category]

    return formatted_receipts

