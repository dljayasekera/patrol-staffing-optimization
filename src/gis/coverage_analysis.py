
import geopandas as gpd
import folium

def build_map(zones_geojson, out_html):
    gdf = gpd.read_file(zones_geojson)
    m = folium.Map(location=[41.58,-93.62], zoom_start=11)

    for _,r in gdf.iterrows():
        folium.CircleMarker(
            location=[r.geometry.y, r.geometry.x],
            radius=3,
            color="red"
        ).add_to(m)

    m.save(out_html)
    print("Saved map:", out_html)

if __name__ == "__main__":
    import sys
    build_map(sys.argv[1], sys.argv[2])
