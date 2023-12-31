from flask import Flask, request, jsonify
import pretty_errors
import pprint
from logging_config import logger as  logging
from a2wsgi import WSGIMiddleware
from main import main


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def index():
    """
    echo endpoint for server health check 
    """
    logging.info(f"{index.__name__} -- INDEX ENDPOINT TRIGGERED -- {request.method}")
    return jsonify({"status": "success", "message": "Hello World!"}), 200


@app.route('/lead_auto_assignment', methods=['POST'])
def lead_auto_assignment():
    """
    lead auto assignment endpoint
    """
    # receiving lead payload
    payload = request.get_json()
    logging.info(f"{lead_auto_assignment.__name__} -- RAW PAYLOAD -- {pprint.pformat(payload)}\n")

    # extracting useful information from the payload
    postalcode = payload.get("listing_zip") if payload.get(
        "listing_zip") != "N/A" else ""
    listing_province = payload.get("listing_province") if payload.get(
        "listing_province") != "N/A" else ""
    listing_city = payload.get("listing_city") if payload.get(
        "listing_city") != "N/A" else ""
    buyer_city = payload.get("buyer_city") if payload.get(
        "buyer_city") != "N/A" else ""
    buyer_province = payload.get("buyer_province") if payload.get(
        "buyer_province") != "N/A" else ""

    logging.info(f"{lead_auto_assignment.__name__} -- POSTALCODE AFTER N/A FORMATTING -- {postalcode}")
    logging.info(f"{lead_auto_assignment.__name__} -- LISTING AFTER N/A FORMATTING -- {listing_province}")
    logging.info(f"{lead_auto_assignment.__name__} -- LISTING AFTER N/A FORMATTING -- {listing_city}")
    logging.info(f"{lead_auto_assignment.__name__} -- BUYER AFTER N/A FORMATTING -- {buyer_province}")
    logging.info(f"{lead_auto_assignment.__name__} -- BUYER CITY AFTER N/A FORMATTING -- {buyer_city}")

    # executing lead auto assignment function; returning result
    result = main(postalcode, listing_province,
                  listing_city, buyer_city, buyer_province)
    
    logging.info(f"{lead_auto_assignment.__name__} -- RESPONSE -- {result}")
    return jsonify(result), 200

# configuring wsgi
app = WSGIMiddleware(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
