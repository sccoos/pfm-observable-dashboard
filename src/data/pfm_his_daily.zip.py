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
from datetime import datetime, timedelta
import pytz

## Read NetCDF file
### Read .nc model output from Falk web server
tempfile = "./web_data_latest.nc"
x = f"https://falk.ucsd.edu/PFM_Forecast/LV4_His/web_data_latest.nc"
urllib.request.urlretrieve(x, tempfile)
ds = xr.open_dataset(tempfile, decode_timedelta=False)

## Sites time series csv
# Extract the sites_dye_tot variable and its coordinates
sites_dye_tot = ds['sites_dye_tot'].values
# Base datetime (e.g., starting point in UTC)
base_datetime = datetime(1999, 1, 1)
pst_datetimes = []
for time in ds['time'].values:
    time_delta = timedelta(days=time.__float__())
    utc_datetime = base_datetime + time_delta
    pst_timezone = pytz.timezone('US/Pacific')
    pst_datetime = pytz.utc.localize(utc_datetime).astimezone(pst_timezone)
    pst_datetimes.append(pst_datetime)

site_info_string = ds.attrs['site info']
site_name_list = site_info_string[23:] # note: because there are 23 characters before the actual information starts
site_names = site_name_list.split(", ")

# Create a pandas DataFrame for the sites dye time series
site_dye_series = pd.DataFrame(sites_dye_tot, columns=site_names)
site_dye_series.insert(0, 'time', pst_datetimes)


## Build geometry objects for contours, shoreline indicators, & sites
all_contours = []
all_shoreline_points = []

contour_lmin = -6
contour_lmax = -1.5
contour_interval = 0.5
color_map = {
    0: 'palegreen',
    1: 'gold',
    2: 'firebrick'
}
risk_thresholds = {
    'low': ds['thresh_holds'][:].values[0],
    'high': ds['thresh_holds'][:].values[1]
}

cmap = plt.get_cmap('RdYlGn') # Define the contour colormap
plevs = np.arange(contour_lmin,contour_lmax,contour_interval) # Define the contour levels
# For all timestamps
for index in range(len(pst_datetimes)):
    fig, ax = plt.subplots()
    cset=ax.contourf(ds['map_lon'],ds['map_lat'],ds['map_l10_dye_tot'][index, :, :], plevs, cmap=cmap.reversed(), extend='max')
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
    plt.close()


# Create a GeoJSON for the site markers
# Create a pandas DataFrame
site_markers = {
    'label': site_names
}
site_markers_df = pd.DataFrame(site_markers)

# Convert to GeoPandas GeoDataFrame
site_markers_geometries = [Point(xy) for xy in zip(ds['sites_lon'].values.tolist(), ds['sites_lat'].values.tolist())]
site_markers = gpd.GeoDataFrame(site_markers_df, geometry=site_markers_geometries).to_json()

### Write zip archive of generated web files
# Create a buffer
zip_buffer = io.BytesIO()

# Write JSON string to the zip file
# contour needs to get chunked into 4 files
split_array = np.array_split(all_contours, 4)
for i, subarray in enumerate(split_array):
    with zipfile.ZipFile(zip_buffer, "a") as zip_file:
        json_string = json.dumps(subarray.tolist())
        zip_file.writestr(f'computed_dye_contours_{i}.json', json_string, compress_type=zipfile.ZIP_DEFLATED)


 # Write JSON string to the zip file
with zipfile.ZipFile(zip_buffer, "a") as zip_file:
    json_string = json.dumps(all_shoreline_points)
    zip_file.writestr("computed_shoreline_points.json", json_string, compress_type=zipfile.ZIP_DEFLATED)

 # Write JSON string to the zip file
with zipfile.ZipFile(zip_buffer, "a") as zip_file:
    json_string = json.dumps(risk_thresholds)
    zip_file.writestr("risk_thresholds.json", json_string, compress_type=zipfile.ZIP_DEFLATED)

# Write DataFrame to a CSV file in the zip file
with zipfile.ZipFile(zip_buffer, mode = "a") as zip_file:
    df_csv_string = site_dye_series.to_csv(index=False)
    zip_file.writestr("site_timeseries.csv", df_csv_string, compress_type=zipfile.ZIP_DEFLATED)

 # Write JSON string to the zip file
with zipfile.ZipFile(zip_buffer, "a") as zip_file:
    json_string = json.dumps(site_markers)
    zip_file.writestr("site_markers.json", json_string, compress_type=zipfile.ZIP_DEFLATED)

# Write the zip file to standard output
# with open('pfm_daily_his.zip', 'wb') as f:
#     f.write(zip_buffer.getvalue())

# Write the zip file to standard output
sys.stdout.buffer.write(zip_buffer.getvalue())