# Investigating Cat Movement Patterns 

## Project goals
This project analyses GPS tracking data from a [Tractive](https://tractive.com/) collar (.gpx from tractive), which is mostly worn by cats and dogs.
The raw data is cleaned and is segmented along two dimensions: day phases (night, dawn, day, dusk) and movement phases (moving vs. static phases).
For day phases and for (non-)static data the home range estimation (KDE) is computed.
In the end, two interactive plots are generated as HTML files.
The first plot shows the home range estimation for different day phases.
The second plot shows the range for (non-)static data.

### Key Analyses
- Home Range Estimation: Kernel Density Estimation (KDE) to compute utilisation distributions (95%, 75%, 50%, 25%, 10%).
- Movement Classification: Distinguishing static (resting) from moving phases using GPS positional accuracy buffers (customised meter radius).

### Product
- Two interactive plots saved as HTML showing the home range estimation (KDE, 95%, 75%, 50%, 25%, 10% UD).
One distinguished by day phases, the other distinguished by (non-)static phases.
Open street map is used as base layer.

## Repository Structure

```
data_tractive/      input datasets from tractive
src/                analysis scripts
plots/              output figures
tests/              test files
.github/workflows   folder containing GitHub actions
```

## Install UV
Installation instructions can be found in the official uv documentation:
https://docs.astral.sh/uv/getting-started/installation/#winget

For Windows: open terminal and run:

```bash
winget install --id=astral-sh.uv  -e
```

For Mac/Linux: open terminal and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Set Up Project

Open terminal in your IDE and run:

```bash
git clone https://github.com/Seleine/SS2026_DSaaP_Project.git
cd SS2026_DSaaP_Project
```

### Home Coordinates
For the protection of sensitive location data, the home coordinates are stored in a separate Python file that is excluded from the GitHub repository via .gitignore.
Therefore, the file `home_coords.py` must be manually created by the user following the structure below:

```python
import geopandas as gpd
from shapely import Point
import config

# Please enter your home coordinates ("Easting", "Northing") in the correct CRS
point = Point(["Easting", "Northing"])

home_coords = gpd.GeoSeries([point], crs=config.CRS)
```
The correct projected CRS can be found on [EPSG.io](https://epsg.io/).

### Config File
The file `config.py` contains several variables which must be provided by the user.

| **Variable Name**   | **Example Value**                          | **Description**                                                                                                                                                                                |
|---------------------|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| buffer_around_home  | 8                                          | The tracking points gathered at home don't reflect reality. Therefore, it is sensible to delete them. This variable determines the radius around the home coordinates which should be deleted. |
| CRS                 | 2056                                       | Projected coordinate reference system                                                                                                                                                          |
| file_path           | "data_tractive"                            | Folder, in which the data is stored.                                                                                                                                                           |
| gpx_layer           | "track_points"                             | Layer name.                                                                                                                                                                                    |
| columns_of_choice   | ["track_seg_point_id", "time", "geometry"] | Columns in the .gpx data set which should be kept.                                                                                                                                             |
| time_zone           | "Europe/Zurich"                            | Time zone of choice.                                                                                                                                                                           |
| max_speed_kmh       | 48                                         | Particular speed limit. Is used to determine implausible data points which will be deleted.                                                                                                    |
| min_timelag_s       | 540                                        | The tractive collar usually sends data in regular intervals. For higher data quality it is sensible to delete data points which are considerably lower than the set interval.                  |
| buffer_intersection | 8                                          | For determining (non-)static phases, a buffer around each data point is needed.                                                                                                                |

### Running the Analysis

Open terminal in your IDE and run:

```bash
uv run src/main.py
```

The resulting plots will appear in the folder «plots».

## Data

The GPS data from [Tractive](https://tractive.com/) must be provided by the user. For calculating the home range at least 50 data points must be provided.
Therefore, the tracker must be worn outside for at least two days.
The folder «data_tractive» contains sample GPS data colleted from a cat.

## Authors

Edina Szöcsik, Thimona Chrusciel, Selina Lepori

ZHAW School of Life Sciences and Facility Management
Institute for Computational Life Sciences
Schloss
8820 Wädenswil 

## License

This project is licensed under the MIT License. See the License file for details.


