import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
# import dotenv
import time
import json
import numpy as np
import os
from utils import add_ghg_emissions, visualise



class data_handler():
    def __init__(self, zone="10YFR-RTE------C", document="A75", process_type="A16", periodstart="201612310000",
                 periodend="201701010000", file_path="data.json"):

        self.endpoint = "https://transparency.entsoe.eu/api?securityToken="
        # self.security_token = dotenv.get_variable(".env", "token")
        self.zone_maping = {
            "10YFR-RTE------C": "France",
            "10YBE----------2": "Belgium",
            "10Y1001A1001A796": "Denmark",
            "10Y1001A1001A83F": "Germany",
            "10Y1001A1001A92E": "United Kingdom",
            "10YNL----------L": "Netherlands",
            "10YES-REE------0": "Spain",
            "10YCH-SWISSGRIDZ": "Switzerland"
        }
        assert zone in self.zone_maping.keys(), "Unknown zone request"

        self.energies_maping = {
            "B01": "Biomass",
            "B02": "Fossil Brown coal/Lignite",
            "B03": "Fossil Coal-derived gas",
            "B04": "Fossil Gas",
            "B05": "Fossil Hard coal",
            "B06": "Fossil Oil",
            "B07": "Fossil Oil shale",
            "B08": "Fossil Peat",
            "B09": "Geothermal",
            "B10": "Hydro Pumped Storage",
            "B11": "Hydro Run-of-river and poundage",
            "B12": "Hydro Water Reservoir",
            "B13": "Marine",
            "B14": "Nuclear",
            "B15": "Other renewable",
            "B16": "Solar",
            "B17": "Waste",
            "B18": "Wind Offshore",
            "B19": "Wind Onshore",
            "B20": "Other"
        }
        if os.path.exists("data.json"):
            self.__load_data()
            if self.zone_maping[zone] in self.complete_data.keys():
                a_dates = list(self.complete_data[self.zone_maping[zone]].keys())
                a_dates = sorted([datetime.strptime(date, "%Y%m%d%H%M") for date in a_dates])
                periodend = (a_dates[-1] + timedelta(days=1)).strftime("%Y%m%d%H%M")
                periodstart = a_dates[-1].strftime("%Y%m%d%H%M")

        else:
            self.complete_data = {self.zone_maping[zone]: {}}

        self.zone = "&In_Domain=" + zone
        self.document = "&documentType=" + document
        self.period_start = "&periodStart=" + periodstart
        self.date_start = datetime.strptime(self.period_start.split("=")[1], "%Y%m%d%H%M")
        self.period_end = "&periodEnd=" + periodend
        self.date_end = datetime.strptime(self.period_end.split("=")[1], "%Y%m%d%H%M")
        self.process_type = "&processType=" + process_type
        self.file_path = file_path

        if self.zone_maping[zone] not in self.complete_data.keys():
            self.complete_data.update({self.zone_maping[zone]: {}})

    def get(self):
        requete = self.endpoint + self.security_token + self.document + self.process_type + self.zone + self.period_start + self.period_end
        print(requete)
        self.data = requests.get(requete).text

    def parse_data(self):
        soup = bs(self.data, features="html.parser")
        psr_data = {}
        for ts in soup.find_all("timeseries"):
            soup_ts = bs(str(ts), features="html.parser")
            hours = soup_ts.find_all("position")
            quantities = soup_ts.find_all("quantity")
            psr_data.update({self.energies_maping[soup_ts.find("psrtype").text]: {hours[k].text: quantities[k].text for
                                                                                  k in range(len(hours))}})
        self.data = {self.period_start.split("=")[1]: psr_data}
        self.__happend_data()

    def get_next_day(self):
        self.date_start = self.date_start + timedelta(days=1)
        self.period_start = "&periodStart=" + self.date_start.strftime("%Y%m%d%H%M")
        self.date_end = self.date_end + timedelta(days=1)
        self.period_end = "&periodEnd=" + self.date_end.strftime("%Y%m%d%H%M")

    def __happend_data(self):
        self.complete_data[self.zone_maping[self.zone.split("=")[1]]].update(self.data)

    def __load_data(self):
        with open(self.file_path, "r") as json_file:
            self.complete_data = json.load(json_file)

    def dump_data(self):
        with open(self.file_path, "w") as json_file:
            json.dump(self.complete_data, json_file)


if __name__ == "__main__":

    with open("data_ghg.json", "r") as json_file:
        data = json.load(json_file)

    visualise(data, "Spain", "202001140000")

    """
    zones = ["10Y1001A1001A83F", "10YFR-RTE------C", "10YNL----------L", "10YES-REE------0", "10YCH-SWISSGRIDZ",
             "10YFR-RTE------C"]
    for country in zones:
        robot = data_handler(zone=country)
        for _ in range(4 * 365):
            robot.get()
            robot.parse_data()
            robot.get_next_day()
            if np.random.random() < 0.05:
                robot.dump_data()
            time.sleep(0.1)
        robot.dump_data()
    """
