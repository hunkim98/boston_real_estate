import bs4 
import requests
import pandas as pd
BASE_URL = "https://www.cityofboston.gov/assessing/search/"

def get_sales_info(pid):
    url = f"{BASE_URL}?pid={pid}"
    print(url)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return soup

def parse_td_with_td_tag_string(soup, string):
    td = soup.find("td", string=string)
    if td:
        # get parent parent
        parent_parent = td.parent
        # get the td that has align="right"
        total_room_num = parent_parent.find("td", {"align": "right"}).text
        return total_room_num
    else:
        return None

def parse_owner_info(soup, search_owner=True):
    owner_table = soup.find("th", string="Current Owner/s")
    if owner_table:
        owner_table = owner_table.parent.parent
        owner_rows = owner_table.find_all("tr")
        owner_row = owner_rows[1] # it is the second row
        owner_name = owner_row.find_all("td")[1].text
        
        if search_owner:
            
            # do a new search
            url = f"{BASE_URL}?owner={requests.utils.quote(owner_name)}"
            # https://www.cityofboston.gov/assessing/search/?owner=141%20ASHLEY%20LLC
            response = requests.get(url)
            owner_soup = bs4.BeautifulSoup(response.text, "html.parser")
            # find table with id = "owner_table"
            owner_table = owner_soup.find("table", {"id": "tblSearchParcels"})
            
            property_rows = owner_table.find_all("tr")
            properties = []
            for property_row in property_rows:
                if property_row.get("class") == ["mainColTableHeaderRow"]:
                    continue
                # for each row the first td is the property id
                tds = property_row.find_all("td")
                property_id = tds[0].text
                property_address = tds[1].text
                properties.append({
                    "parcel": property_id,
                    "address": property_address
                })
            return owner_name, properties
        else:
            return owner_name, None
    else:
        return None, None
    
def process_basic_info(soup, search_owner=True):
    total_room_num = parse_td_with_td_tag_string(soup, "Total Rooms:")
    bedrooms = parse_td_with_td_tag_string(soup, "Bedrooms:")
    bathrooms = parse_td_with_td_tag_string(soup, "Bathrooms:")
    half_bathrooms = parse_td_with_td_tag_string(soup, "Half Bathrooms:")
    kitchens = parse_td_with_td_tag_string(soup, "Number of Kitchens:")
    fireplaces = parse_td_with_td_tag_string(soup, "Fireplaces:")
    ac_type = parse_td_with_td_tag_string(soup, "AC Type:")
    heat_type = parse_td_with_td_tag_string(soup, "Heat Type:")
    interior_condition = parse_td_with_td_tag_string(soup, "Interior Condition:")
    parking_spots = parse_td_with_td_tag_string(soup, "Parking Spots:")
    year_built = parse_td_with_td_tag_string(soup, "Year Built:")
    exterior_condition = parse_td_with_td_tag_string(soup, "Exterior Condition:")
    foundation = parse_td_with_td_tag_string(soup, "Foundation:")
    full_address = parse_td_with_td_tag_string(soup, "Address:")
    
    owner_name, properties = parse_owner_info(soup, search_owner)
    if properties is not None:
        owner_property_count = len(properties)
    else:
        owner_property_count = None
    
    return {
        "total_room_num": total_room_num,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "half_bathrooms": half_bathrooms,
        "kitchens": kitchens,
        "fireplaces": fireplaces,
        "ac_type": ac_type,
        "heat_type": heat_type,
        "interior_condition": interior_condition,
        "parking_spots": parking_spots,
        "year_built": year_built,
        "exterior_condition": exterior_condition,
        "foundation": foundation,
        "full_address": full_address,
        "owner_name": owner_name,
        "owner_property_count": owner_property_count,
        "properties": properties
    }


if __name__ == "__main__":
    PDF_FOLDER = "data/2019"
    PDF_FILENAME = "merged_sales.csv"
    data = pd.read_csv(f"{PDF_FOLDER}/{PDF_FILENAME}")

    # Create a list to store all the new information
    new_data = []
        

    for idx, row in data.iterrows():
        print(f"Processing {idx + 1}/{len(data)}: {row['parcel']}")
        try:
            # Get the property information
            soup = get_sales_info(row["parcel"].replace("-", ""))
            info = process_basic_info(soup)
            
            # Combine existing row data with new info
            combined_data = row.to_dict()
            combined_data.update(info)
            
            # Remove the properties list as it's not needed in the main dataframe
            if 'properties' in combined_data:
                del combined_data['properties']
                
            new_data.append(combined_data)
            
        except Exception as e:
            print(f"Error processing {row['parcel']}: {str(e)}")
            # Add the original row data with None values for new fields
            combined_data = row.to_dict()
            combined_data.update({
                "total_room_num": None,
                "bedrooms": None,
                "bathrooms": None,
                "half_bathrooms": None,
                "kitchens": None,
                "fireplaces": None,
                "ac_type": None,
                "heat_type": None,
                "interior_condition": None,
                "parking_spots": None,
                "year_built": None,
                "exterior_condition": None,
                "foundation": None,
                "full_address": None,
                "owner_name": None,
                "owner_property_count": None
            })
            new_data.append(combined_data)
        # if idx > 15:
        #     break
    # Create new dataframe
    new_df = pd.DataFrame(new_data)

    # Save to CSV
    new_df.to_csv(f"{PDF_FOLDER}/enriched_{PDF_FILENAME}", index=False)
    print("Data processing complete. Saved to enriched_sales_data.csv")

    # get_sales_info(2101833138)