import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
from datetime import datetime, timedelta
import random

# Charger stops
stops = pd.read_csv("casablanca_stops.csv", encoding='utf-8-sig')
stops['geometry'] = stops['geometry'].apply(wkt.loads)
stops_gdf = gpd.GeoDataFrame(stops, geometry='geometry', crs='EPSG:4326')

# Charger routes
routes = pd.read_csv('casablanca_bus_tram_routes.csv', encoding='utf-8-sig')
routes['geometry'] = routes['geometry'].apply(wkt.loads)
routes_gdf = gpd.GeoDataFrame(routes, geometry='geometry', crs='EPSG:4326')

# Projection métrique pour calculer les distances en mètres
stops_proj = stops_gdf.to_crs(epsg=32629)
routes_proj = routes_gdf.to_crs(epsg=32629)

# Distance max tolérée entre stop et ligne
max_distance = 20  # en mètres

matches = []

for idx_stop, stop_row in stops_proj.iterrows():
    stop_point = stop_row.geometry
    routes_proj['dist'] = routes_proj.geometry.distance(stop_point)
    nearby_routes = routes_proj[routes_proj['dist'] <= max_distance]

    for idx_route, route_row in nearby_routes.iterrows():
        # Génération aléatoire de données dynamiques
        vehicle_id = f"veh_{random.randint(1000, 9999)}"
        trip_id = f"trip_{random.randint(5000, 9999)}"

        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        speed_kmh = round(random.uniform(0, 60), 1)

        eta_next_stop = timestamp + timedelta(minutes=random.randint(1, 15))
        eta_next_stop_str = eta_next_stop.strftime("%Y-%m-%d %H:%M:%S")

        occupancy_level = random.choice(['low', 'medium', 'high'])
        status = random.choice(['on_time', 'delayed', 'early'])
        delay_seconds = random.randint(-300, 900)

        matches.append({
            'route_id': route_row['route_id'],
            'route_name': route_row['route_name'],
            'route_type': route_row['route_type'],
            'stop_id': stop_row['stop_id'],
            'stop_name': stop_row['stop_name'],
            'latitude': stop_point.y,
            'longitude': stop_point.x,
            'vehicle_id': vehicle_id,
            'trip_id': trip_id,
            'timestamp': timestamp_str,
            'speed_kmh': speed_kmh,
            'eta_next_stop': eta_next_stop_str,
            'occupancy_level': occupancy_level,
            'status': status,
            'delay_seconds': delay_seconds
        })

matches_df = pd.DataFrame(matches)

# Reprojection pour garantir les bonnes coordonnées géographiques
stops_wgs = stops_proj.to_crs(epsg=4326)
matches_df['latitude'] = matches_df.apply(
    lambda row: stops_wgs.loc[stops_wgs['stop_id'] == row['stop_id'], 'geometry'].values[0].y, axis=1)
matches_df['longitude'] = matches_df.apply(
    lambda row: stops_wgs.loc[stops_wgs['stop_id'] == row['stop_id'], 'geometry'].values[0].x, axis=1)

# Export CSV en UTF-8 avec BOM (compatible Excel + accents OK)
matches_df.to_csv('trips3.csv', index=False, encoding='utf-8-sig')

print(f"trips3.csv généré avec {len(matches_df)} lignes.")
