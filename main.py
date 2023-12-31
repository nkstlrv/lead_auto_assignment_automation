import json
from random import randint
import pretty_errors
from logging_config import logger as  logging
from utils import prepare_postalcode, get_not_excluded_realtors
from db.postgres import p_queries as postgres
from db.mysql import m_queries as mysql


def main(postalcode: str, listing_province: str, listing_city: str, buyer_city: str, buyer_province: str) -> dict:
    """
    the main function that executes full lead auto assignment cycle
    """
    response = {
        "realtor_1": 0,
        "realtor_emails": [],
        "assigned_realtor": "willow@fb4s.com"
    }

    province = listing_province if listing_province not in (None, "") else buyer_province
    city = listing_city if listing_city not in (None, "") else buyer_city
    # formatting postal code to the desired format -- A1A1A1 -> A1A 1A1
    postalcode = prepare_postalcode(postalcode)

    logging.info(f"{main.__name__} -- SEARCH PROVINCE -- {province}")
    logging.info(f"{main.__name__} -- SEARCH CITY -- {city}")
    logging.info(f"{main.__name__} -- SEARCH POSTAL CODE -- {postgres}")

    # searching in additional cities
    additional_cities = postgres.get_additional_cities_by_city_province(city=buyer_city, province=province)
    logging.info(f"{main.__name__} -- FOUND ADDITIONAL CITIES -- {additional_cities}")

    # if found in additional cities -> returning those realtor
    if len(additional_cities) > 0:
        response["realtor_1"] = 1
        for city in additional_cities:
            response["realtor_emails"].append(city[3])

        # evaluation assigned realtor to the Round-Robin logic
        assigned_realtor = postgres.get_realtor_to_assign(response["realtor_emails"])
        logging.info(f"{main.__name__} -- ROUND-ROBIN ASSIGNED REALTOR -- {assigned_realtor}")

        if len(assigned_realtor) > 0:
            response["assigned_realtor"] = assigned_realtor[-1][0]
        else:
            # if no round-robin assigner realtor -> evaluation randomly
            response["assigned_realtor"] = response["realtor_emails"][randint(
                0, len(response["realtor_emails"]) - 1)]
    
    # nobody found in additional cities
    else:
        # searching for realtors in overlapping polygons
        realtors_in_polygon = [
            realtor[2] for realtor in mysql.get_realtors_in_polygon(city, province, postalcode)]
        logging.info(f"{main.__name__} -- FOUND REALTORS IN POLYGON -- {realtors_in_polygon}")

        if len(realtors_in_polygon) > 0:
            # searching for realtors who's city is NOT excluded
            not_excluded_realtors = get_not_excluded_realtors(
                buyer_city, province, realtors_in_polygon)
            logging.info(f"{main.__name__} -- NOT EXCLUDED REALTORS -- {not_excluded_realtors}")

            # realtors found in overlapping polygon; returning them
            if len(not_excluded_realtors) > 0:

                response["realtor_1"] = 1
                for realtor in not_excluded_realtors:
                    response["realtor_emails"].append(realtor)

                # evaluation assigned realtor to the Round-Robin logic
                assigned_realtor = postgres.get_realtor_to_assign(response["realtor_emails"])
                logging.info(f"{main.__name__} -- ROUND-ROBIN ASSIGNED REALTOR -- {assigned_realtor}")

                if len(assigned_realtor) > 0:
                    response["assigned_realtor"] = assigned_realtor[-1][0]
                else:
                    response["assigned_realtor"] = response["realtor_emails"][randint(
                        0, len(response["realtor_emails"]) - 1)]

    return response


if __name__ == "__main__":
    main("N/A", "N/A", "N/A", "N/A", "N/A", "N/A")
