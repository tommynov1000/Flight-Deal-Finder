import pandas
import math
# This class is responsible for talking to the Google Sheet.


class DataManager:

    def __init__(self):
        self.flights = pandas.read_csv("places.csv").replace({math.nan: None}).to_dict("records")
        self.users = pandas.read_csv("users.csv").to_dict("records")

    def save_data(self):
        df = pandas.DataFrame.from_records(self.flights)
        df.to_csv("places.csv", index=False)
