import os
import datetime as dt

class FlightData:
    def __init__(self, trip_type: str, from_city: str, from_code: str, to_city: str, to_code: str, price: int,
                 fly_date: str, return_date: str, links: list):
        self.trip_type = trip_type
        self.origin_city = from_city
        self.origin_code = from_code
        self.destination_city = to_city
        self.destination_code = to_code
        self.total_price = price
        self.leave_date = fly_date
        self.return_date = return_date
        self.links = links
