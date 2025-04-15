# import urllib
# from netCDF4 import Dataset

# ### Read .nc model output from Falk web server
# new_x = "/data/tmp/temp.nc"
# x = "https://falk.ucsd.edu/PFM_Forecast/LV4_His/web_data_2025041206.nc"
# urllib.request.urlretrieve(x, new_x)

# # Open the NetCDF file
# nc_file = Dataset(new_x, mode='r')




# ### Write zip archive of generated web files
# # Create a buffer
# zip_buffer = io.BytesIO()

# # Write JSON string to the zip file
# with zipfile.ZipFile(zip_buffer, "w") as zip_file:
#     zip_file.writestr("file_name.json", earthquake_meta_json)

# # Write DataFrame to a CSV file in the zip file
# with zipfile.ZipFile(zip_buffer, "a") as zip_file:
#     df_csv_string = earthquakes_df.to_csv(index=False)
#     zip_file.writestr("quakes.csv", df_csv_string)

# # Write the zip file to standard output
# sys.stdout.buffer.write(zip_buffer.getvalue())