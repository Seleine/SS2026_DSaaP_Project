import geopandas as gpd
import numpy as np
from scipy.stats import gaussian_kde
from shapely.geometry import Polygon
from shapely import union_all
from skimage import measure
import pyproj


def extract_coords(data: gpd.GeoDataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract x and y coordinates from a GeoDataFrame's geometry column.

    Args:
        data (GeoDataFrame): Input GeoDataFrame with point geometries
                             in a projected metric CRS (e.g. EPSG:2056).

    Returns:
        tuple[np.ndarray, np.ndarray]: A tuple of (x, y) coordinate arrays.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError("Argument data must be a gpd.GeoDataFrame")

    # make sure the correct geometry column is set
    data = data.set_geometry("geometry")

    # extract the single points (x, y) from the geometry column
    coords = np.array([(geom.x, geom.y) for geom in data.geometry])
    x, y = coords[:, 0], coords[:, 1]

    return x, y


def fit_kde(x: np.ndarray, y: np.ndarray) -> gaussian_kde:
    """
    Fit KDE on coordinates of GPS data points.

    Args:
        x (np.ndarray): Input for x coordinates.
        y (np.ndarray): Input for y coordinates.

    Returns:
        gaussian_kde: A fitted KDE object using Scott's rule for bandwidth selection.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
        raise TypeError("Arguments x and y must be a np.ndarray")

    # fit KDE (bandwidth via Scott's rule, same default as kernelUD 'href' (cf. R code))
    # KDE learns the shape of the distribution of the GPS points
    kde = gaussian_kde(
        np.vstack([x, y])
    )  # matrix: nrows = 2, ncols = number of GPS points

    return kde


def build_evaluation_grid_for_kde(
    x: np.ndarray, y: np.ndarray, grid_size: int = 200
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build evaluation grid for kde.

    Args:
        x (np.ndarray): Input for x coordinates.
        y (np.ndarray): Input for y coordinates.
        grid_size (int): Resolution of the KDE evaluation grid. Defaults to 200.

    Returns:
        tuple[np.ndarray, np.ndarray]: A tuple of (xi, yi) evenly spaced grid tick.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
        raise TypeError("Arguments x and y must be a np.ndarray")

    # build a regular 2D evaluation grid over the area where the points are
    margin = 0.05  # 5% padding around the point extent, so that points at the edge don't get clipped
    # create the bounding box
    x_range = x.max() - x.min()
    y_range = y.max() - y.min()

    # xi and yi are 200 evenly spaced values (ticks) along the longitude and latitude in the area of the bounding box
    xi = np.linspace(x.min() - margin * x_range, x.max() + margin * x_range, grid_size)
    yi = np.linspace(y.min() - margin * y_range, y.max() + margin * y_range, grid_size)

    return xi, yi


def build_meshgrid_for_kde(
    xi: np.ndarray, yi: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build meshgrid for kde.

    Args:
        xi (np.ndarray): Evenly spaced grid ticks along the x axis.
        yi (np.ndarray): Evenly spaced grid ticks along the y axis.

    Returns:
        tuple[np.ndarray, np.ndarray]: A tuple (Xi, Yi) of coordinate matrices from coordinate vectors.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if not isinstance(xi, np.ndarray) or not isinstance(yi, np.ndarray):
        raise TypeError("Arguments xi and yi must be a np.ndarray")

    # combine xi and yi to a 2D grid
    # Xi repeats the x-values across each row, Yi repeats the y-values down each column
    # So at any position [i, j], the pair (Xi[i,j], Yi[i,j]) gives you the exact coordinates of that grid cell.
    Xi, Yi = np.meshgrid(xi, yi)

    return Xi, Yi


def evaluate_kde(kde: gaussian_kde, Xi: np.ndarray, Yi: np.ndarray) -> np.ndarray:
    """
    Evaluate the kde.

    Args:
        kde (gaussian_kde): A fitted KDE object using Scott's rule for bandwidth selection.
        Xi (np.ndarray): Coordinate matrix for x axis.
        Yi (np.ndarray): Coordinate matrix for y axis.

    Returns:
        np.ndarray: A 2D density surface evaluated at each grid cell.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if not isinstance(kde, gaussian_kde):
        raise TypeError("Argument kde must be a gaussian_kde")
    if not isinstance(Xi, np.ndarray) or not isinstance(Yi, np.ndarray):
        raise TypeError("Arguments Xi and Yi must be a np.ndarray")

    # 2D grid (Xi, Yi) is fed in to the kde function to get a density value at every grid cell.
    # 2D array is flattened into a 1D array and stacked into a matrix with two rows
    # each column is one grid point as an (x, y) pair. -> this is the format gaussian_kde expects (dimensions, n_points)
    positions = np.vstack([Xi.ravel(), Yi.ravel()])
    # evaluate KDE at all positions, returns a flat array. reshape turns back into a matrix.
    Zi = kde(positions).reshape(Xi.shape)  # Zi = density surface

    return Zi


def normalise_kde(Zi: np.ndarray) -> np.ndarray:
    """
    Normalise to a probability surface.

    Args:
        Zi (np.ndarray): A 2D density surface evaluated at each grid cell.

    Returns:
        np.ndarray: A normalised 2D probability surface.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if not isinstance(Zi, np.ndarray):
        raise TypeError("Argument Zi must be a np.ndarray")

    Zi_norm = Zi / Zi.sum()

    return Zi_norm


def contour_to_polygons(
    contour: np.ndarray, xi: np.ndarray, yi: np.ndarray
) -> Polygon | None:
    """
    Convert contour paths to shapely polygons.

    Args:
        contour (np.ndarray): Represent contour lines with shape (n, 2) -> representing points.
        xi (np.ndarray): Evenly spaced grid ticks along the x axis.
        yi (np.ndarray): Evenly spaced grid ticks along the y axis.

    Returns:
        Polygon | None: A Shapely Polygon if valid, otherwise None.

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if (
        not isinstance(xi, np.ndarray)
        or not isinstance(yi, np.ndarray)
        or not isinstance(contour, np.ndarray)
    ):
        raise TypeError("Arguments contour, Xi, and Yi must be a np.ndarray")

    # find_contours returns (row, col), need to convert back to (x, y) coordinates
    x_coords = xi[contour[:, 1].astype(int)]
    y_coords = yi[contour[:, 0].astype(int)]
    coords = np.column_stack(
        [x_coords, y_coords]
    )  # returns shape (n, 2) -> each row is one (x, y) point
    if (
        len(coords) < 4
    ):  # only possible to get a polygon with 3 points (for shapely first and last point must be identical to close the polygon).
        return None
    try:
        poly = Polygon(coords)
        return (
            poly if poly.is_valid and poly.area > 0 else None
        )  # return True if a geometry is well-formed
    except Exception:
        return None


def extract_contour_polygons(
    xi: np.ndarray,
    yi: np.ndarray,
    Zi_norm: np.ndarray,
    variable_name: str,
    crs: pyproj.CRS,
    percentiles: list[int] = [95, 75, 50, 25, 10],
) -> gpd.GeoDataFrame:
    """
    Extract contour polygons for each percentile.

    Args:
        xi (np.ndarray): Evenly spaced grid ticks along the x axis.
        yi (np.ndarray): Evenly spaced grid ticks along the y axis.
        Zi_norm (np.ndarray): A normalised 2D probability surface.
        crs (pyproj.CRS): coordinate reference system of the data.
        percentiles (list[int]): Probability contour levels to extract. Defaults to [95, 75, 50, 25, 10].

    Returns:
        gpd.GeoDataFrame: One row per percentile with columns percent (int), geometry (Polygon | MultiPolygon), and area_km2 (float).

    Raises:
        TypeError: If argument is the wrong data type.
    """
    if (
        not isinstance(xi, np.ndarray)
        or not isinstance(yi, np.ndarray)
        or not isinstance(Zi_norm, np.ndarray)
    ):
        raise TypeError("Arguments xi, yi, and Zi_norm must be np.ndarray")

    flat_sorted = np.sort(
        Zi_norm.ravel()
    )[
        ::-1
    ]  # flatten grid to 1D array, deselect spatial position and sort from highest to lowest density
    cumsum = np.cumsum(
        flat_sorted
    )  # cumsum needed for selecting the thresholds [95, 75, 50, 25, 10]

    records = []

    for pct in percentiles:  # [95, 75, 50, 25, 10]
        threshold_idx = np.searchsorted(
            cumsum, pct / 100.0
        )  # gets the index of the percentile in the cumsum array
        threshold = flat_sorted[
            min(threshold_idx, len(flat_sorted) - 1)
        ]  # returns threshold at which the contour line should be drawn (single density value)

        # finds the lines where the surface equals threshold
        contours = measure.find_contours(Zi_norm, level=threshold)

        # convert contour paths to Shapely polygons
        polygons = [
            poly
            for contour in contours
            if (poly := contour_to_polygons(contour, xi, yi)) is not None
        ]

        if polygons:
            # returns the union of multiple geometries
            # handles the case where the density surface has multiple disconnected regions
            # would return a MultiPolygon
            merged = union_all(polygons)
            records.append(
                {
                    "percent": pct,
                    "geometry": merged,
                    "area_km2": merged.area / 1e6,
                    "Variable": variable_name,
                }
            )

    ########################
    # Return as GeoDataFrame
    ########################
    ranges = gpd.GeoDataFrame(records, crs=crs)

    return ranges


def calculate_kde_from_gps_points(
    data: gpd.GeoDataFrame,
    variable_name: str,
    percentiles: list[int] = [95, 75, 50, 25, 10],
    grid_size: int = 200,
) -> gpd.GeoDataFrame:
    """
    Calculate Kernel Density Estimation from GPS Points.

    Args:
        data (GeoDataFrame): Input GeoDataFrame with point geometries
                             in a projected metric CRS (e.g. EPSG:2056).
        variable_name (str): Input name for variable.
        percentiles (list[int]): Probability contour levels to extract.
                                 Defaults to [95, 75, 50, 25, 10].
        grid_size (int): Resolution of the KDE evaluation grid.
                         Higher values produce smoother contours but are slower.
                         Defaults to 200.

    Returns:
        GeoDataFrame: One row per percentile with columns:
                      - percent (int): the probability level
                      - geometry: polygon or multipolygon of the home range
                      - area_km2 (float): area of the home range in km2
    """

    if len(data) < 50:
        raise ValueError(
            f"At least 50 GPS points required for reliable KDE estimation, got {len(data)}."
        )

    if percentiles is None:
        percentiles = [95, 75, 50, 25, 10]

    x, y = extract_coords(data)
    kde = fit_kde(x, y)
    xi, yi = build_evaluation_grid_for_kde(x, y, grid_size)
    Xi, Yi = build_meshgrid_for_kde(xi, yi)
    Zi = evaluate_kde(kde, Xi, Yi)
    Zi_norm = normalise_kde(Zi)

    return extract_contour_polygons(
        xi=xi,
        yi=yi,
        Zi_norm=Zi_norm,
        variable_name=variable_name,
        crs=data.crs,
        percentiles=percentiles,
    )
