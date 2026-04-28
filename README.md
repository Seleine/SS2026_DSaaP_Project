# DSaaP Project

## What this Project does
This project analyses GPS tracking data from a [Tractive](https://tractive.com/) collar (.gpx from tractive), which is mostly worn by cats and dogs.
The data is cleaned and day phases (night, dawn, day, dusk) and (non-)static phases are computed.
For day phases and for (non-)static data the home range estimation (KDE) is computed.
In the end, two interactive plots are generated as HTML files.
The first plot shows the home range estimation for different day phases.
The second plot shows the range for (non-)static data.
For calculating the home range at least 50 data points must be provided.
Therefore, the tracker must be worn outside for at least two days.
The purpose is to find out more about the behaviour of the individuum wearing the tracker.

### Key Analyses
- Home Range Estimation: Kernel Density Estimation (KDE) to compute utilisation distributions (95%, 75%, 50%, 25%, 10%).
- Movement Classification: Distinguishing static (resting) from moving phases using GPS positional accuracy buffers (customised meter radius).

### Product
- Two interactive plots saved as HTML showing the home range estimation (KDE, 95%, 75%, 50%, 25%, 10% UD).
One distinguished by day phases, the other distinguished by (non-)static phases.
Open street map is used as base layer.

## Repository Structure


Brief overview of the repository layout.

```
data_tractive/      input datasets from tractive
src/                analysis scripts
plots/              output figures
tests/              test files
.github/workflows   folder containing GitHub actions
```

## Set Up Project
- Install UV: https://docs.astral.sh/uv/getting-started/installation/#winget
- to run project after installing uv enter in terminal: `uv run main.py`
Describe how to set up the environment and dependencies.

Example:

```
git clone https://github.com/Seleine/SS2026_DSaaP_Project.git
cd SS2026_DSaaP_Project

conda env create -f environment.yml
conda activate project-env
```

### Home Coordinates
For data security, the home coordinates are stored in a separate Python file which won't be uploaded to GitHub.
Therefore, the file `home_coords.py` has to be created and looks as follows:

```python
import geopandas as gpd
from shapely import Point
import src.customised_variables

# Please enter your home coordinates ("Easting", "Northing") in the correct CRS
point = Point(["Easting", "Northing"])

home_coords = gpd.GeoSeries([point], crs=src.customised_variables.CRS)
```

### Customised Variables
The file `customised_variables.py` contains several variables which needs to be provided by the user.

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

## Running the Analysis


Explain the minimal steps needed to run the project.

Example:

```
python scripts/run_analysis.py
```

or

```
snakemake --cores 4
```

State where results will appear.

## Data

Describe where the data comes from.

* Is the data included in the repository?
* If not, where can it be downloaded?
* Provide accession numbers or links if applicable.

Example:

Dataset available from GEO

## Authors

Edina Szöcsik, Thimona Chrusciel, Selina Lepori

ZHAW School of Life Sciences and Facility Management
Institute for Computational Life Sciences
Schloss
8820 Wädenswil 

## License

This project is licensed under the <LICENCENAME> License – see the LICENSE file for details.


