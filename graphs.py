from math import radians, cos, sin, asin, sqrt, floor
from places import fetch_photo_url
import random

_WALKING_SPEED = 5.5
_TAKE_PATHS = 3


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


def path_distance(s, distances):
    path_dist = 0
    for a, b in zip(s, s[1:]):
        path_dist += distances[a][b]
    return path_dist


def place_rank(place):
    return place.get('rating', 2.5)


def path_rank(path, places):
    rank = 0
    for place in path[1:-1]:
        rank += place_rank(places[place - 2]) / 5

    if rank == 0:
        return 0

    same_type_penalty_ratio = 0.3
    same_type_penalty = len(path) - 2
    for place1, place2 in zip(path[1:-1], path[2:-1]):
        if places[place1 - 2]['types'][0] == places[place2 - 2]['types'][0]:
            same_type_penalty -= 1

    return 5 * (same_type_penalty_ratio * same_type_penalty + (1 - same_type_penalty_ratio) * rank) / (len(path) - 2)


def generate_possible_path(path, distances, duration):
    new_path = path

    if len(distances) == 2:
        return new_path

    number_of_returns = 50
    while True:
        edge = random.randrange(1, len(new_path))

        new_node = random.randrange(2, len(distances))
        if new_node in new_path:
            new_node = random.randrange(2, len(distances))
        new_path = new_path[:edge] + [new_node] + new_path[edge:]

        if path_distance(new_path, distances) > duration:
            new_path = new_path[:edge] + new_path[edge + 1:]
            number_of_returns -= 1
            if number_of_returns == 0:
                break

    return new_path


def generate_possible_updated_path(path, distances, duration):
    new_path = path

    number_of_returns = 50
    while True:
        edge = random.randrange(1, len(new_path))

        new_node = random.randrange(2, len(distances))
        if new_node in new_path:
            new_node = random.randrange(2, len(distances))
        new_path = new_path[:edge] + [new_node] + new_path[edge:]

        if path_distance(new_path, distances) > duration:
            new_path = new_path[:edge] + new_path[edge + 1:]
            number_of_returns -= 1
            if number_of_returns == 0:
                break

    return new_path


def generate_minimal_path(path, distances, duration):
    new_path = path

    number_of_returns = 50
    while True:
        edge = random.randrange(1, len(new_path))

        min_new_distance = -1
        min_new_node = None
        for next_node in range(2, len(distances)):
            if next_node in new_path:
                continue

            if not min_new_node or min_new_distance > distances[new_path[edge - 1]][next_node] + distances[next_node][edge]:
                min_new_node = next_node
                min_new_distance = distances[new_path[edge - 1]][next_node] + distances[next_node][edge]

        new_path = new_path[:edge] + [min_new_node] + new_path[edge:]

        if path_distance(new_path, distances) > duration:
            new_path = new_path[:edge] + new_path[edge + 1:]
            number_of_returns -= 1
            if number_of_returns == 0:
                break

    return new_path


def string_time(time):
    h = int(floor(time))
    m = int(floor((time - h) * 60))

    return '{} hour{}, {} minute{}'.format(h, '' if h == 1 else 's', m, '' if m == 1 else 's')


def beautify(loc_in, loc_out, path, distances, places):
    data = [{'lon': loc_in[0], 'lat': loc_in[1]}]

    for p in path[1:-1]:
        place = places[p - 2]
        data.append({
            'lon': place['geometry']['location']['lng'],
            'lat': place['geometry']['location']['lat'],
            'photo_url': fetch_photo_url(place),
            'name': place['name'],
            'place_type': place['place_type'],
        })

    data.append({'lon': loc_out[0], 'lat': loc_out[1]})

    return {'duration': string_time(path_distance(path, distances)), 'path': data}


def generate_paths(loc_in, loc_out, places_data, duration):
    places = places_data[0]
    place_durations = [0, 0] + places_data[1]
    locations = places_data[2]
    all_locations = [loc_in, loc_out] + locations

    distances = [[place_durations[i] for i, _ in enumerate(range(len(all_locations)))] for _ in range(len(all_locations))]

    for i, place1 in enumerate(all_locations):
        for j, place2 in enumerate(all_locations):
            distances[i][j] += haversine(place1[0], place1[1], place2[0], place2[1]) / _WALKING_SPEED

    # We don't need all of this Dijkstra's mumbo jumbo since we know the shortest path is [0, 1] (attributes of graph)
    # q = set(list(range(len(all_locations))))
    # dist = [10000000 for _ in range(len(all_locations))]
    # prev = [None for _ in range(len(all_locations))]
    # dist[0] = 0
    # while q:
    #
    #     m = -1
    #     u = None
    #     for k in q:
    #         if m is -1 or dist[k] < m:
    #             m = dist[k]
    #             u = k
    #
    #     q.remove(u)
    #
    #     for v in range(len(all_locations)):
    #         if u == v:
    #             continue
    #         alt = dist[u] + distances[u][v]
    #         if alt < dist[v]:
    #             dist[v] = alt
    #             prev[v] = u

    base_path = [0, 1]
    # while prev[u]:
    #     s = [u] + s
    #     u = prev[u]
    # s = [0, u] + s

    path_dist = path_distance(base_path, distances)

    # if the minimum path is already over our limit, return it
    if path_dist > duration:
        return beautify(loc_in, loc_out, base_path, distances, places)

    possible_paths = []
    for _ in range(10):
        possible_paths.append(generate_possible_path(base_path, distances, duration))

    # for possible_path in possible_paths:
    #     print(possible_path, path_distance(possible_path, distances), path_rank(possible_path, places))

    final_paths = list(map(lambda l: l[1], list(sorted([(path_rank(path, places), path) for path in possible_paths]))[::-1][:_TAKE_PATHS]))
    # print(final_paths)
    return [beautify(loc_in, loc_out, path, distances, places) for path in final_paths]

    # print('=====')
    # possible_paths = []
    # for _ in range(10):
    #     possible_paths.append(generate_minimal_path(s, distances, duration))
    #
    # for possible_path in possible_paths:
    #     print(possible_path, path_distance(possible_path, distances), path_rank(possible_path, places))

