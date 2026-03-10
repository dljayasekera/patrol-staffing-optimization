
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def build_geo(input_file, out_geojson):
    df = pd.read_excel(input_file)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    gdf.to_file(out_geojson, driver="GeoJSON")
    print("Saved GeoJSON:", out_geojson)

if __name__ == "__main__":
    import sys
    build_geo(sys.argv[1], sys.argv[2])
