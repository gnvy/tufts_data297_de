import pandas as pd
import folium
from folium.plugins import HeatMap
import http.server
import socketserver
import webbrowser
import threading
import time

# Load data
bike_data = pd.read_csv('data/bikeshare_data/202410-bluebikes-tripdata.csv')

# Station popularity
start_station_popularity = bike_data.groupby(['start_station_name', 'start_lat', 'start_lng']).size().reset_index(name='start_count')
end_station_popularity = bike_data.groupby(['end_station_name', 'end_lat', 'end_lng']).size().reset_index(name='end_count')


station_popularity = start_station_popularity.merge(
    end_station_popularity, 
    left_on=['start_station_name', 'start_lat', 'start_lng'],
    right_on=['end_station_name', 'end_lat', 'end_lng'],
    how='outer'
)

# Clean up the merged data
station_popularity['station_name'] = station_popularity['start_station_name'].fillna(station_popularity['end_station_name'])
station_popularity['lat'] = station_popularity['start_lat'].fillna(station_popularity['end_lat'])
station_popularity['lng'] = station_popularity['start_lng'].fillna(station_popularity['end_lng'])
station_popularity['total_trips'] = station_popularity['start_count'].fillna(0) + station_popularity['end_count'].fillna(0)


center_lat = station_popularity['lat'].mean()
center_lng = station_popularity['lng'].mean()

m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

for idx, row in station_popularity.iterrows():
    radius = min(row['total_trips'] / 100, 20)  
    
    folium.CircleMarker(
        location=[row['lat'], row['lng']],
        radius=radius,
        popup=f"""
        <b>{row['station_name']}</b><br>
        Total Trips: {row['total_trips']:,}<br>
        Starts: {row['start_count']:,}<br>
        Ends: {row['end_count']:,}
        """,
        color='blue',
        fill=True,
        fillOpacity=0.6
    ).add_to(m)

m.save('bike_station_popularity.html')


def start_server():
    PORT = 8000
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
time.sleep(2)
webbrowser.open(f'http://localhost:8000/bike_station_popularity.html')