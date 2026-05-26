
# To compare with JPL Horizon's data, create a CSV file with the collected data
import requests
import csv
import re

# Horizons API endpoint
url = "https://ssd.jpl.nasa.gov/api/horizons.api"

# Query parameters
params = {
    "format": "text",
    "COMMAND": "'Ceres'",
    "EPHEM_TYPE": "'VECTORS'",
    "CENTER": "'500@0'",            #SSB
    "START_TIME": "'1999-12-29'",   #Defined start (at midnight)
    "STOP_TIME": "'2010-01-03'",    #Defined stop
    "STEP_SIZE": "'1 d'",
    "TIME_TYPE": "'TDB'",           #Barycentric Dynamical Time 
    "VEC_TABLE": "'2'",
    "OUT_UNITS": "'KM-S'"
}

# Download Horizons output
response = requests.get(url, params=params)
response.raise_for_status()

text = response.text

# Extract only the ephemeris block
start = text.find("$$SOE")
end = text.find("$$EOE")

data_block = text[start:end]

lines = data_block.splitlines()

rows = []

# Parse every vector entry
for i in range(len(lines)):

    # Position line
    if "X =" in lines[i]:
        pos_line = lines[i]

        # Velocity line follows immediately after
        vel_line = lines[i + 1]

        x = float(re.search(r"X =\s*([\-\d.E+]+)", pos_line).group(1))
        y = float(re.search(r"Y =\s*([\-\d.E+]+)", pos_line).group(1))
        z = float(re.search(r"Z =\s*([\-\d.E+]+)", pos_line).group(1))

        vx = float(re.search(r"VX=\s*([\-\d.E+]+)", vel_line).group(1))
        vy = float(re.search(r"VY=\s*([\-\d.E+]+)", vel_line).group(1))
        vz = float(re.search(r"VZ=\s*([\-\d.E+]+)", vel_line).group(1))

        rows.append([x, y, z, vx, vy, vz])


# Write CSV file
with open("Ceres_JPL_vectors_10yrs_1day.csv", "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["x", "y", "z", "vx", "vy", "vz"])
    writer.writerows(rows)

print(f"CSV file created with {len(rows)} rows")

# 367 rows were created, which is the same length as the data (states_array) created by Tudat for TU3
# (in the same time frame)