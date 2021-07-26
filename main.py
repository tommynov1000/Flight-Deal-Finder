from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
import datetime as dt

ORIGIN_CITY_IATA = "RDU"
NUMBER_OF_NIGHTS_MIN = 4
NUMBER_OF_NIGHTS_MAX = 7

# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve
# the program requirements.

data_manager = DataManager()
from_time = dt.datetime.now() + dt.timedelta(days=1)
to_time = dt.datetime.now() + dt.timedelta(days=(6 * 30))

flight_search = FlightSearch()
notification_manager = NotificationManager

for city in data_manager.flights:
    if city["IATA Code"] is None:
        city["IATA Code"] = flight_search.get_IATA_code(city["City"])

    print(f"Searching for prices to {city['IATA Code']}")

    flight = flight_search.find_cheapest_flight(
        origin=ORIGIN_CITY_IATA,
        destination=city["IATA Code"],
        from_time=from_time,
        to_time=to_time
    )

    if flight != f"No flights found to {city['IATA Code']}":
        print(f"Found flight for {flight.total_price}")
        if flight.total_price <= city["Lowest Price"]:
            print("Found cheap price! Sending email!\n")
            for user in data_manager.users:
                notification_manager.send_msg(flight, user)
    else:
        print(flight + "\n")
