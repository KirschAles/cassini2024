import folium
from geopy import distance

# Center coordinates (Prague)
center_lat, center_lon = 50.08705, 14.42492

# Create a base map
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# Calculate rectangle corners
half_height = 1.75  # 3.5km / 2
half_width = 2.5  # 5km / 2

north = distance.distance(kilometers=half_height).destination((center_lat, center_lon), bearing=0)
south = distance.distance(kilometers=half_height).destination((center_lat, center_lon), bearing=180)
east = distance.distance(kilometers=half_width).destination((center_lat, center_lon), bearing=90)
west = distance.distance(kilometers=half_width).destination((center_lat, center_lon), bearing=270)

# Define rectangle bounds
sw_corner = [south.latitude, west.longitude]
ne_corner = [north.latitude, east.longitude]

# Add a rectangle to the map
folium.Rectangle(
    bounds=[sw_corner, ne_corner],
    color='red',
    fill=True,
    fillColor='red',
    fillOpacity=0.2
).add_to(m)

# Add a marker at the center
folium.Marker([center_lat, center_lon], popup="Center").add_to(m)

# Save the map
m.save('map_with_centered_rectangle.html')
