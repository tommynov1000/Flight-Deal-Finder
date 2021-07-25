import os
import requests
import datetime as dt
from flight_data import FlightData

HEADERS = {
    "apikey": os.environ["TEQUILA_AUTH_KEY"]
}
NIGHTS_IN_DST_FROM = 4
NIGHTS_IN_DST_TO = 7
TEQUILA_ENDPOINT = "https://tequila-api.kiwi.com"


def find_cheapest_oneway(origin: str, destination: str, from_time: dt.datetime, to_time: dt.datetime,
                         endpoint: str):
    results = []
    from_time_formatted = from_time.strftime("%d/%m/%Y")
    to_time_formatted = to_time.strftime("%d/%m/%Y")
    query = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": from_time_formatted,
        "date_to": to_time_formatted,
        "flight_type": "oneway",
        "adults": 1,
        "one_for_city": 1,
        "curr": "USD",
        "stopover_to": "4:00",
    }
    response = requests.get(url=endpoint, headers=HEADERS, params=query)
    response.raise_for_status()
    results.append(response.json())

    try:
        arrival_date = results[0]["data"][0]["local_arrival"].split("T")[0].split("-")
    except IndexError:
        results = []
        return results
    else:
        dt_arrival_date = dt.datetime(year=int(arrival_date[0]), month=int(arrival_date[1]), day=int(arrival_date[2]))

    from_time_nights_in_from = dt_arrival_date + dt.timedelta(NIGHTS_IN_DST_FROM)
    from_time_nights_in_from_formatted = from_time_nights_in_from.strftime("%d/%m/%Y")
    to_time_nights_in_to = dt_arrival_date + dt.timedelta(NIGHTS_IN_DST_TO)
    to_time_nights_in_to_formatted = to_time_nights_in_to.strftime("%d/%m/%Y")
    query = {
        "fly_from": destination,
        "fly_to": origin,
        "date_from": from_time_nights_in_from_formatted,
        "date_to": to_time_nights_in_to_formatted,
        "flight_type": "oneway",
        "adults": 1,
        "one_for_city": 1,
        "curr": "USD",
        "stopover_to": "4:00",
    }
    response = requests.get(url=endpoint, headers=HEADERS, params=query)
    response.raise_for_status()
    results.append(response.json())

    return results


def find_cheapest_round(origin: str, destination: str, from_time: dt.datetime, to_time: dt.datetime,
                        endpoint: str):
    from_time_formatted = from_time.strftime("%d/%m/%Y")
    to_time_formatted = to_time.strftime("%d/%m/%Y")
    query = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": from_time_formatted,
        "date_to": to_time_formatted,
        "nights_in_dst_from": NIGHTS_IN_DST_FROM,
        "nights_in_dst_to": NIGHTS_IN_DST_TO,
        "flight_type": "round",
        "adults": 1,
        "one_for_city": 1,
        "curr": "USD",
        "stopover_to": "4:00",
    }
    response = requests.get(url=endpoint, headers=HEADERS, params=query)
    response.raise_for_status()
    return response.json()


class FlightSearch:

    @staticmethod
    def get_IATA_code(city_name):
        locations_endpoint = f"{TEQUILA_ENDPOINT}/locations/query"
        query = {
            "term": city_name,
            "location_types": "city",
        }
        response = requests.get(url=locations_endpoint, headers=HEADERS, params=query)
        response.raise_for_status()
        data = response.json()

        is_null = True
        index = 0
        while is_null:
            if data["locations"][index]["code"] is None:
                index += 1
            else:
                is_null = False

        return data["locations"][index]["code"]

    @staticmethod
    def find_cheapest_flight(origin: str, destination: str, from_time: dt.datetime, to_time: dt.datetime):
        print(f"Finding cheapest flights to {destination}")
        price_endpoint = f"{TEQUILA_ENDPOINT}/v2/search"
        results_oneway = find_cheapest_oneway(origin, destination, from_time, to_time, price_endpoint)
        results_round = find_cheapest_round(origin, destination, from_time, to_time, price_endpoint)

        try:
            data_oneway_part1 = results_oneway[0]["data"][0]
            data_oneway_part2 = results_oneway[1]["data"][0]
        except IndexError:
            oneway_found = False
        else:
            oneway_found = True
            oneway_price = data_oneway_part1["price"] + data_oneway_part2["price"]
        try:
            data_round = results_round["data"][0]
        except IndexError:
            round_found = False
        else:
            round_price = data_round["price"]
            round_found = True

        if round_found and oneway_found:
            if oneway_price > round_price:
                return_round = True
            else:
                return_round = False
        elif round_found:
            return_round = True
        elif oneway_found:
            return_round = False
        else:
            return f"No flights found to {destination}"

        if return_round:
            route_length = len(data_round["route"])
            print("Creating round itinerary\n")
            flight_data = FlightData(
                trip_type="round",
                from_city=data_round["cityFrom"],
                from_code=data_round["cityCodeFrom"],
                to_city=data_round["cityTo"],
                to_code=data_round["cityCodeTo"],
                price=round_price,
                fly_date=data_round["utc_departure"].split("T")[0],
                return_date=data_round["route"][route_length - 1]["utc_departure"].split("T")[0],
                links=[data_round["deep_link"]]
            )
        else:
            print("Creating oneway itinerary\n")
            flight_data = FlightData(
                trip_type="oneway",
                from_city=data_oneway_part1["cityFrom"],
                from_code=data_oneway_part1["cityCodeFrom"],
                to_city=data_oneway_part1["cityTo"],
                to_code=data_oneway_part1["cityCodeTo"],
                price=oneway_price,
                fly_date=data_oneway_part1["utc_departure"].split("T")[0],
                return_date=data_oneway_part2["utc_departure"].split("T")[0],
                links=[data_oneway_part1["deep_link"], data_oneway_part2["deep_link"]]
            )

        return flight_data
