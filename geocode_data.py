from arcgis.gis import GIS
from arcgis.geocoding import geocode
from arcgis.geometry import Point
import pandas as pd

def geocode_address(address):
    gis = GIS()
    results = geocode(address)
    if results:
        location = results[0]['location']
        point = Point(location)
        x = point.x
        y = point.y
        return x, y
    else:
        print(f"No results found for {address}")
        return None, None

if __name__ == "__main__":
    # read the data
    CSV_FOLDER = "data/2019"
    PDF_FILENAME = "enriched_merged_sales.csv"
    data = pd.read_csv(f"{CSV_FOLDER}/{PDF_FILENAME}")
    # get the full address
    # use iterrows to iterate over the dataframe
    for idx, row in data.iterrows():
        # print the progress
        print(f"Processing {idx} of {len(data)}")
        full_address = row["full_address"]
        x, y = geocode_address(full_address)
        # update the dataframe
        data.loc[idx, "x"] = x
        data.loc[idx, "y"] = y
    # save the dataframe
    data.to_csv(f"{CSV_FOLDER}/geocoded_{PDF_FILENAME}", index=False)