from arcgis.gis import GIS
from arcgis.geocoding import geocode
from arcgis.geometry import Point
from arcgis.mapping import WebMap
from arcgis.features import Feature, FeatureSet
from arcgis.mapping import MapView

# Connect anonymously
gis = GIS()

# Geocode an address
address = "1600 Amphitheatre Parkway, Mountain View, CA"
results = geocode(address)

if results:
    location = results[0]['location']
    point = Point(location)

    # Define a colored symbol (e.g., red diamond)
    symbol = {
        "type": "esriSMS",
        "style": "esriSMSDiamond",
        "color": [255, 0, 0, 255],  # Red in RGBA
        "size": 12,
        "outline": {"color": [0, 0, 0, 255], "width": 1}
    }

    # Create a feature with the symbol
    feature = Feature(geometry=point, symbol=symbol)
    feature_set = FeatureSet([feature])

    # Display on the map
    map_view = gis.map(location['y'], location['x'], zoomlevel=15)
    map_view

    map_view.draw(feature_set)
else:
    print("Address not found.")
