import urllib
import xarray as xr
import pandas as pd
import geojsoncontour
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import numpy as np
import zipfile
import io
import sys

## Read NetCDF file
### Read .nc model output from Falk web server
# TODO need to use dynamic datestring
tempfile = "/data/tmp/temp.nc"
x = "https://falk.ucsd.edu/PFM_Forecast/LV4_His/LV4_ocean_his_202504160000.nc" 
urllib.request.urlretrieve(x, tempfile)
ds = xr.open_dataset(tempfile, decode_timedelta=True)

## Sites time series csv
# Extract the sites_dye_tot variable and its coordinates
sites_dye_tot = ds['sites_dye_tot'].values
times = ds['time'].values
site_names = ds['sites_lat'].values  # Assuming site names correspond to latitudes .. TODO matt should add site_names to .nc

# Create a pandas DataFrame for the sites dye time series
site_dye_series = pd.DataFrame(sites_dye_tot, columns=site_names)
site_dye_series.insert(0, 'time', times)


## Build geometry objects for contours & shoreline indicators
all_contours = []
all_shoreline_points = []

color_map = {
    0: 'palegreen',
    1: 'gold',
    2: 'firebrick'
}
cmap = plt.get_cmap('RdYlGn') # Define the contour colormap
plevs = np.arange(-6,-1.5,.5) # Define the contour levels
# For all timestamps
for index in range(len(times)):
    fig, ax = plt.subplots()
    cset=ax.contourf(ds['map_lon'],ds['map_lat'],np.log10( ds['map_dye_tot'][index,:,:] ), plevs, cmap=cmap.reversed())
    contour_geojson = geojsoncontour.contourf_to_geojson(
        contourf=cset,
        ndigits=8
    )
    #array of json contour features for each timestamp
    all_contours.append(contour_geojson)

    # Create a GeoJSON for the shoreline points
    colors = [color_map[number.values.__int__()] for number in ds['shoreline_risk'][index, :]]
    # Create a pandas DataFrame
    shoreline = {
        'risk': colors
    }
    shoreline_df = pd.DataFrame(shoreline)

    # Convert to GeoPandas GeoDataFrame
    shoreline_geometries = [Point(xy) for xy in zip(ds['shoreline_lon'].values.tolist(), ds['shoreline_lat'].values.tolist())]
    gdf = gpd.GeoDataFrame(shoreline_df, geometry=shoreline_geometries)
    all_shoreline_points.append(gdf.to_json())

# TODO write these arrays of json to files
# with open(f'./data/all_dye_contours.json', 'w') as f:
#     json.dump(all_contours, f)
# with open(f'./data/all_shore_points.json', 'w') as f:
#     json.dump(all_shoreline_points, f)

# # TODO write site timeseries csv to file
# output_csv_path = './data/sites_dye_tot.csv'
# site_dye_series.to_csv(output_csv_path, index=False)


### Write zip archive of generated web files
# Create a buffer
zip_buffer = io.BytesIO()

# Write JSON string to the zip file
with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    zip_file.writestr("computed_dye_contours.json", all_contours)

 # Write JSON string to the zip file
with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    zip_file.writestr("computed_shoreline_points.json", all_shoreline_points)

# Write DataFrame to a CSV file in the zip file
with zipfile.ZipFile(zip_buffer, "a") as zip_file:
    df_csv_string = site_dye_series.to_csv(index=False)
    zip_file.writestr("site_timeseries.csv", df_csv_string)

# Write the zip file to standard output
sys.stdout.buffer.write(zip_buffer.getvalue())