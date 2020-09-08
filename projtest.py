from pyproj import Proj
import pyproj
from pyproj import CRS
import math
crs = CRS.from_epsg(4326)
p1 = Proj('+proj=cart +ellps=WGS84')
p2 = Proj(proj='cart',ellps='WGS84')
lon = 116.2627707
lat = 40.0825987
hell = 25.965
x = 652954.1006
y = 4774619.7919
z = -2217647.7937

ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
x, y, z = pyproj.transform(lla, ecef, lon, lat, hell, radians=True)

# print lat, lon, alt
print(x,y,z)


grs80 = (6378137, 298.257222100882711)
wgs84 = (6378137, 298.257223563)


def geodetic_to_geocentric(ellps, lat, lon, h):
    """
    Compute the Geocentric (Cartesian) Coordinates X, Y, Z
    given the Geodetic Coordinates lat, lon + Ellipsoid Height h
    """
    a, rf = ellps
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    N = a / math.sqrt(1 - (1 - (1 - 1 / rf) ** 2) * (math.sin(lat_rad)) ** 2)
    X = (N + h) * math.cos(lat_rad) * math.cos(lon_rad)
    Y = (N + h) * math.cos(lat_rad) * math.sin(lon_rad)
    Z = ((1 - 1 / rf) ** 2 * N + h) * math.sin(lat_rad)

    return(X, Y, Z)
print(geodetic_to_geocentric(wgs84, lat, lon, hell))

