import osmnx as ox
import pandas as pd

city_name = "Casablanca, Morocco"

tags = {
    'highway': 'bus_stop',
    'railway': 'tram_stop'
}

stops = ox.features_from_place(city_name, tags)
stops_df = stops.reset_index()

stops_df = stops_df[['id', 'name', 'geometry']]

# Projection UTM 29N pour calculer les centroides correctement
stops_proj = stops_df.to_crs(epsg=32629)
stops_df['lon'] = stops_proj['geometry'].centroid.x
stops_df['lat'] = stops_proj['geometry'].centroid.y

stops_df.rename(columns={'id': 'stop_id', 'name': 'stop_name'}, inplace=True)

# Sauvegarde au format CSV
stops_df.to_csv("casablanca_stops_osm.csv", index=False, encoding='utf-8-sig')
