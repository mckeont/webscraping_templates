import requests
import pandas as pd
import folium

# Overpass API endpoint
url = "https://overpass-api.de/api/interpreter"

# Overpass QL query
query = """
[out:json][timeout:25];
area["name"="Boston"]["boundary"="administrative"]["admin_level"="8"]->.searchArea;
(
  node["amenity"="restaurant"]["cuisine"~"vietnamese", i](area.searchArea);
  way["amenity"="restaurant"]["cuisine"~"vietnamese", i](area.searchArea);
  relation["amenity"="restaurant"]["cuisine"~"vietnamese", i](area.searchArea);
);
out center tags;
"""

# Send the request
response = requests.get(url, params={'data': query})
data = response.json()

# Parse the data
restaurants = []
for el in data['elements']:
    tags = el.get('tags', {})
    name = tags.get('name', 'Unnamed')
    cuisine = tags.get('cuisine', '')
    
    # Coordinates vary slightly by type
    if 'lat' in el and 'lon' in el:
        lat, lon = el['lat'], el['lon']
    elif 'center' in el:
        lat, lon = el['center']['lat'], el['center']['lon']
    else:
        continue

    restaurants.append({
        'Name': name,
        'Cuisine': cuisine,
        'Latitude': lat,
        'Longitude': lon
    })

# Save to CSV
df = pd.DataFrame(restaurants)
df.to_csv("osm_vietnamese_boston.csv", index=False)
print(f" Bun bo hue Saved {len(restaurants)} restaurants to 'osm_vietnamese_boston.csv'")

# Create a map
map_boston = folium.Map(location=[42.36, -71.06], zoom_start=13)
for r in restaurants:
    folium.Marker(
        location=[r['Latitude'], r['Longitude']],
        popup=f"{r['Name']}<br>{r['Cuisine']}"
    ).add_to(map_boston)

map_boston.save("osm_vietnamese_boston_map.html")
print("Map saved as 'osm_vietnamese_boston_map.html'")
