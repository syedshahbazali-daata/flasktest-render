from flask import Flask, request, jsonify
import requests
import re
import json
import os

app = Flask(__name__)


# Function to get shop_id based on URL
def get_shop_id(url):
    try:
        if url[-1] == '/':
            url = url[:-1]
        res = requests.get(f"{url}/shop.json")
        res.raise_for_status()
        shop_id = re.search(r"shop_id: (\d+)", res.text).group(1)
        return shop_id
    except requests.RequestException as e:
        print(f"Failed to get shop ID: {e}")
        return None


# Function to fetch authorization token
def get_authorization():
    if os.path.exists("authorization.json"):
        with open("authorization.json", "r") as f:
            authorization = json.load(f).get("authorization")
            return authorization
    return None


# Flask route to fetch authorization
@app.route('/api/get_authorization', methods=['GET'])
def api_get_authorization():
    try:
        res = requests.get("https://67051d5c031fd46a830eb344.mockapi.io/api/1")
        res.raise_for_status()
        # save in a file
        with open("authorization.json", "w") as f:
            json.dump(res.json(), f)
            return jsonify({"message": "Authorization saved successfully"}), 200
    except requests.RequestException as e:
        print(f"Failed to get authorization", e)
        return jsonify({"error": "Failed to get authorization"}), 500
    return jsonify({"error": "Failed to save authorization"}), 500


# Flask route to fetch shop_id from a given URL
@app.route('/api/get_shop_id', methods=['POST'])
def api_get_shop_id():
    data = request.json
    shop_url = data.get('shop_url')
    if not shop_url:
        return jsonify({"error": "Shop URL is required"}), 400

    shop_id = get_shop_id(shop_url)
    if shop_id:
        return jsonify({"shop_id": shop_id}), 200
    return jsonify({"error": "Shop ID not found"}), 404


# Helper function to make API requests
def make_request(url, payload, authorization):
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": authorization,
        "content-type": "application/json",
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None

def make_get_request(url, authorization):
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": authorization,
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None


# Flask route to start tracking a shop
@app.route('/api/start_tracking', methods=['POST'])
def api_start_tracking():
    data = request.json
    shop_id = data.get('shop_id')
    authorization = get_authorization()

    if not shop_id:
        return jsonify({"error": "Shop ID is required"}), 400

    if authorization:
        result = make_request("https://app.shophunter.io/prod/shopify/start", {"override_with_shop_id": shop_id},
                              authorization)
        if result:
            return jsonify({"message": f"Shop with ID: {shop_id} added to tracking"}), 200
        return jsonify({"error": "Failed to start tracking"}), 500

    return jsonify({"error": "Authorization failed"}), 401


# Flask route to stop tracking a shop
@app.route('/api/stop_tracking', methods=['POST'])
def api_stop_tracking():
    data = request.json
    shop_id = data.get('shop_id')
    authorization = get_authorization()

    if not shop_id:
        return jsonify({"error": "Shop ID is required"}), 400

    if authorization:
        result = make_request("https://app.shophunter.io/prod/shops/delete", {"shop_id": shop_id}, authorization)
        if result:
            return jsonify({"message": f"Shop with ID: {shop_id} has been deleted"}), 200
        return jsonify({"error": "Failed to stop tracking"}), 500

    return jsonify({"error": "Authorization failed"}), 401


# Flask route to view store details
@app.route('/api/view_store', methods=['POST'])
def api_view_store():
    data = request.json
    shop_id = data.get('shop_id')
    authorization = get_authorization()

    if not shop_id:
        return jsonify({"error": "Shop ID is required"}), 400

    if authorization:
        store_data = make_request("https://app.shophunter.io/prod/shops/view", {"shop_id": shop_id}, authorization)
        if store_data:
            return jsonify(store_data), 200
        return jsonify({"error": "Failed to get store data"}), 500

    return jsonify({"error": "Authorization failed"}), 401


# Flask route to get chart data for a shop
@app.route('/api/get_chart_data', methods=['POST'])
def api_get_chart_data():
    data = request.json
    shop_id = data.get('shop_id')
    authorization = get_authorization()

    if not shop_id:
        return jsonify({"error": "Shop ID is required"}), 400

    if authorization:
        chart_data = make_request("https://app.shophunter.io/prod/shops/chart",
                                  {"shop_id": shop_id, "timeframe": "day"}, authorization)
        if chart_data:
            return jsonify(chart_data), 200
        return jsonify({"error": "Failed to get chart data"}), 500

    return jsonify({"error": "Authorization failed"}), 401


# Flask route to get products of a shop
@app.route('/api/get_products', methods=['POST'])
def api_get_products():
    data = request.json
    shop_id = data.get('shop_id')
    authorization = get_authorization()

    if not shop_id:
        return jsonify({"error": "Shop ID is required"}), 400

    if authorization:
        products_data = make_request("https://app.shophunter.io/prod/shops/products",
                                     {"shop_id": shop_id, "stub": True}, authorization)
        if products_data:
            return jsonify(products_data), 200
        return jsonify({"error": "Failed to get products data"}), 500

    return jsonify({"error": "Authorization failed"}), 401


def start_tracking(shop_id):
    authorization = get_authorization()
    if authorization:
        url = "https://app.shophunter.io/prod/shopify/start"
        payload = {"override_with_shop_id": shop_id}
        result = make_request(url, payload, authorization)
        if result:
            print(f"Started tracking shop with ID: {shop_id}")
        else:
            print(f"Failed to start tracking shop with ID: {shop_id}")
    else:
        print("Authorization failed")


def stop_tracking(shop_id):
    authorization = get_authorization()
    if authorization:
        url = "https://app.shophunter.io/prod/shops/delete"
        payload = {"shop_id": shop_id}
        result = make_request(url, payload, authorization)
        if result:
            print(f"Stopped tracking shop with ID: {shop_id}")
        else:
            print(f"Failed to stop tracking shop with ID: {shop_id}")
    else:
        print("Authorization failed")


# Flask route to fetch all data (combining multiple requests)
@app.route('/api/get_all_store_data', methods=['POST'])
def api_get_all_store_data():
    data = request.json
    shop_url = data.get('shop_url')

    if not shop_url:
        return jsonify({"error": "Shop URL is required"}), 400

    shop_id = get_shop_id(shop_url)
    if not shop_id:
        return jsonify({"error": "Shop ID not found"}), 404

    authorization = get_authorization()
    if not authorization:
        return jsonify({"error": "Authorization failed"}), 401

    start_tracking(shop_id)
    base_store_data = make_request("https://app.shophunter.io/prod/shops/view", {"shop_id": shop_id}, authorization)
    chart_data = make_request("https://app.shophunter.io/prod/shops/chart", {"shop_id": shop_id, "timeframe": "day"},
                              authorization)
    products_data = make_request("https://app.shophunter.io/prod/shops/products", {"shop_id": shop_id, "stub": True},
                                 authorization)
    stop_tracking(shop_id)

    return jsonify({
        "base_store_data": base_store_data,
        "chart_data": chart_data,
        "products_data": products_data
    }), 200


# Fetch route to get Data of Top Performaning Stores
@app.route('/api/get_top_performing_stores', methods=['GET'])
def api_get_top_performing_stores():
    authorization = get_authorization()
    if not authorization:
        return jsonify({"error": "Authorization failed"}), 401

    url = "https://app.shophunter.io/prod/a/stores/top"

    result = make_get_request(url, authorization)

    if result:
        return jsonify(result), 200
    return jsonify({"error": "Failed to get top performing stores"}), 500

if __name__ == '__main__':
    app.run(debug=True)
