from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


class Distances(object):
    def __init__(self, places):
        self.places = places

        self.distances = [[0 for _ in range(len(places))] for _ in range(len(places))]

        for i, place1 in enumerate(places):
            for j, place2 in enumerate(places):
                self.distances[i][j] = haversine(place1[0], place1[1], place2[0], place2[1])
