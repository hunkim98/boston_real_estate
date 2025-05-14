from arcgis.gis import GIS
from arcgis.geocoding import geocode
from arcgis.geometry import Point

gis = GIS()
address = "141  ASHLEY ST BOSTON MA 02128"
results = geocode(address)

if results:
    location = results[0]['location']
    point = Point(location)
    print(f"Point geometry: {point}")
else:
    print("Address not found.")
