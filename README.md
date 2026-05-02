# DSaaP Project

## What this Project does
This project analyses GPS tracking data from a Tractive collar (.gpx from tractive).
The data is cleaned and day phases and (non-)static phases are computed.
For day phases and for (non-)static data the home range estimation (KDE) is computed.
In the end, two interactive plots are generated as HTML files.
The first plot shows the home range estimation for different day phases.
The second plot shows the range for (non-)static data.

### Key Analyses
- Home Range Estimation: Kernel Density Estimation (KDE) to compute utilisation distributions (95%, 75%, 50%, 25%, 10%).
- Movement Classification: Distinguishing static (resting) from moving phases using GPS positional accuracy buffers (customised meter radius).

### Product
- Interactive plot saved as HTML showing the home range estimation (KDE, 95%, 75%, 50%, 25%, 10% UD).
- Two plots, one showing the home range estimation distinguished by dayphases, the other distinguished by (non-)static phases.

## Set Up Project
- Install UV: https://docs.astral.sh/uv/getting-started/installation/#winget
- to run project after installing uv enter in terminal: `uv run main.py`

### Home Coordinates
For data security, the home coordinates are stored in a separate Python file which won't be uploaded to GitHub.
Therefore, the file `home_coords.py` has to be created and looks as follows:

```python
import geopandas as gpd
from shapely import Point
import customised_variables

# Please enter your home coordinates ("Easting", "Northing") in the correct CRS
point = Point(["Easting", "Northing"])

home_coords = gpd.GeoSeries([point], crs=customised_variables.CRS)
```

### Customised Variables
The file `customised_variables.py` contains several variables which can be edited by the user.
- buffer_around_home: The tracking points gathered at home don't reflect reality. Therefore, it is sensible to delete them. This variable determines the radius around the home coordinates which should be deleted.
- CRS: Projected coordinate reference system
- file_path: Folder, in which the data is stored.
- gpx_layer: Layer name.
- columns_of_choice: Columns in the .gpx data set which should be kept.
- time_zone: Time zone of choice.
- max_speed_kmh: Particular speed limit. Is used to determine implausible data points which will be deleted.
- min_timelag_s: The tractive collar usually sends data in regular intervals. For higher data quality it is sensible to delete data points which are considerably lower than the set interval.
- buffer_intersection: For determining (non-)static phases, a buffer around each data point is needed.


## How to: set up
### Git Repo
Clone directly inside VS Code (GUI)
1. Open VS Code
2. Press Ctrl+Shift+P / Cmd+Shift+P
3. Type Git: Clone
4. Paste the repo URL: https://github.com/Seleine/SS2026_DSaaP_Project
5. Choose a folder on you local computer to save the project
6. Click Open

### Environment setup
#### Exact reproduction (recommended)
Use our frozen version of the environment. 
```bash
conda env create -f environment.lock.yml
conda activate DSAAP_env
```

#### Download newest version of libraries
Use the .yml file to set up the environment. This will install the latest package versions.
```bash
conda env create -f environment.yml
conda activate DSAAP_env
```
