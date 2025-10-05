import overpy
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, box
import time
from overpy import RelationWay

def query_area(api, bbox):
    query = f"""
    [out:json][timeout:180];
    (
      relation["route"="bus"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      relation["route"="tram"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
    );
    out body;
    >;
    out skel qt;
    """
    return api.query(query)

def main():
    api = overpy.Overpass(url="https://overpass.kumi.systems/api/interpreter")
    # Exemple bbox Casablanca approximative (lon_min, lat_min, lon_max, lat_max)
    casablanca_bbox = (-7.72, 33.49, -7.49, 33.65)

    # Diviser bbox en 4 pour exemple
    lon_min, lat_min, lon_max, lat_max = casablanca_bbox
    lons = [lon_min, (lon_min+lon_max)/2, lon_max]
    lats = [lat_min, (lat_min+lat_max)/2, lat_max]

    all_relations = []

    for i in range(len(lons)-1):
        for j in range(len(lats)-1):
            bbox = (lons[i], lats[j], lons[i+1], lats[j+1])
            print(f"Requête pour bbox {bbox}")
            try:
                result = query_area(api, bbox)
                print(f"Relations récupérées dans bbox: {len(result.relations)}")
                all_relations.extend(result.relations)
            except Exception as e:
                print(f"Erreur lors de la requête bbox {bbox}: {e}")
            time.sleep(10)  # pause entre requêtes

    print(f"Total relations récupérées: {len(all_relations)}")

    # Processer all_relations comme dans le script précédent
    routes_data = []
    for rel in all_relations:
        lines = []
        for member in rel.members:
            if isinstance(member, RelationWay) and member.role in ['forward', 'backward', '']:
                way = member.resolve()
                if way and way.nodes:
                    points = [(float(node.lon), float(node.lat)) for node in way.nodes]
                    if len(points) > 1:
                        lines.append(LineString(points))
        if not lines:
            continue
        if len(lines) == 1:
            geometry = lines[0]
        else:
            geometry = MultiLineString(lines)

        route_name = rel.tags.get('name', f'route_{rel.id}')
        route_type = rel.tags.get('route', 'unknown')

        routes_data.append({
            'route_id': rel.id,
            'route_name': route_name,
            'route_type': route_type,
            'geometry': geometry
        })

    print(f"Routes valides extraites: {len(routes_data)}")

    if not routes_data:
        print("Aucune route valide trouvée, fin du script.")
        return

    import geopandas as gpd
    gdf = gpd.GeoDataFrame(routes_data, geometry='geometry', crs='EPSG:4326')

    gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.wkt)
    gdf.to_csv('casablanca_bus_tram_routes.csv', index=False, encoding='utf-8-sig')

    print("Export CSV terminé.")

if __name__ == '__main__':
    main()
