from flask import Flask, request, jsonify
from weather import Weather
from places import Places
from graphs import generate_paths

app = Flask(__name__)


@app.route('/api/', methods=['GET'])
def api():
    lat_in = request.args.get('lat_in', -1)
    lon_in = request.args.get('lon_in', -1)
    lat_out = request.args.get('lat_out', -1)
    lon_out = request.args.get('lon_out', -1)
    duration = request.args.get('duration', -1)

    place_type_filter = request.args.get('types', 'art_gallery, bar, cafe, church, events, library, museum, park, restaurant, zoo'.split(', '))

    if lat_in == -1 or lon_in == -1 or lat_out == -1 or lon_out == -1 or duration == -1:
        return False, 404

    in_weather = Weather(lat_in, lon_in)
    out_weather = Weather(lat_out, lon_out)
    places = Places(lat_in, lon_in, in_weather.bad_weather or out_weather.bad_weather)
    places.filter(place_type_filter)

    paths = generate_paths((float(lon_in), float(lat_in)), (float(lon_out), float(lat_out)), places.data(), float(duration))

    return jsonify({
        'bad_weather': in_weather.bad_weather or out_weather.bad_weather,
        'paths': paths
    }), 201


if __name__ == '__main__':
    app.run(debug=True)
