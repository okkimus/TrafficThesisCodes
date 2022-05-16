# -*- coding: utf-8 -*-

import itertools
import json

_JSON = {}

def get_tms_stations(path, sensor_path):
    "Return a GeoJson of Finnish traffic measurements points"
    global _JSON
    if _JSON:
        return _JSON

    
    with open(path) as f:
        stations = json.load(f)

    with open(sensor_path) as f:
        sensors = json.load(f)

    sensor_lookup = {station['roadStationId']: station['sensorConstantValues'] for station in sensors['tmsStations']}
    # Join the sensor-data with stations
    for feature in stations['features']:
        props = feature['properties']
        props['sensorConstantValues'] = {
            key: list(grouper) 
            for key, grouper in itertools.groupby(
                sensor_lookup[props['roadStationId']],
                key=lambda e: e['name']
                )
        }
        
        long, lat = feature['geometry']['coordinates'][:2]
        props['coords'] = (lat, long)

    _JSON = stations
    return stations


_PROVINCES = {
    1: 'Uusimaa',
    2: 'Varsinais-Suomi',
    6: 'Pirkanmaa',
    4: 'Satakunta',
    8: 'Kymenlaakso',
    9: 'Etelä-Karjala',
    5: 'Kanta-Häme',
    7: 'Päijät-Häme',
    10: 'Etelä-Savo',
    12: 'Pohjois-Karjala',
    11: 'Pohjois-Savo',
    13: 'Keski-Suomi',
    15: 'Pohjanmaa',
    14: 'Etelä-Pohjanmaa',
    16: 'Keski-Pohjanmaa',
    17: 'Pohjois-Pohjanmaa',
    18: 'Kainuu',
    19: 'Lappi',
}
_ELY_CENTERS_FOR_PROVINCE = {
    2: 2,
    6: 4,
}

def get_ely_centers(*tms_numbers):
    stations = get_tms_stations()
    return {
        feature['properties']['tmsNumber']: _ELY_CENTERS_FOR_PROVINCE[int(feature['properties']['provinceCode'])]
        for feature in stations['features']
        if feature['properties']['tmsNumber'] in tms_numbers
    }
