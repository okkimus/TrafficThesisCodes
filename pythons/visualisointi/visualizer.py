import json
import os
import numpy as np

from copy import deepcopy

from mapboxgl_notebook.map import MapboxMap
from mapboxgl_notebook.sources import GeoJSONSource
from mapboxgl_notebook.layers import PointCircleLayer
from mapboxgl_notebook.interactions import ClickInteraction
from mapboxgl_notebook.properties import Paint, Layout

from tms_helpers import get_tms_stations

def create_mapbox():
    # Must be a public token, starting with `pk`
    access_token = 'YOUR_TOKEN_HERE'

    stations = get_tms_stations(path="tms-stations.json", sensor_path="tms-sensor-constants.json")

    source1 = GeoJSONSource(stations, source_id='points1')

    paint = Paint(
        circle_radius=5,
        circle_color="blue",
    )

    circles = PointCircleLayer(source1, paint=paint)
    click = ClickInteraction(circles, properties=['name', 'tmsNumber', 'roadStationId', 'geometry', 'Tien_suunta', 'VVAPAAS1', 'VVAPAAS2', 'direction1Municipality', 'direction2Municipality', 'coords'])

    # https://pypi.org/project/mapboxgl-notebook/
    mapbox_map = MapboxMap(
        access_token=access_token,
        style='mapbox://styles/mapbox/streets-v11',
        zoom=11,
        center=[22.186667, 60.491389],
        sources=[source1],  # can be list of sources
        layers=[circles],  # can be list of layers
        interactions=[click],
    )
    return (mapbox_map, stations)

def create_mapbox_with_classifications(X, y):
    classes = np.unique(y)

    # Must be a public token, starting with `pk`
    access_token = 'YOUR_TOKEN_HERE'

    stations = get_tms_stations(path="tms-stations.json", sensor_path="tms-sensor-constants.json")
    feats = stations["features"]
    lam_ids = []
    for s in stations["features"]:
        lam_ids.append(s["properties"]["tmsNumber"])

    result_features = []
    colors = ["blue", "green", "red", "yellow", "orange"]

    for i in range(len(classes)):
        c = classes[i]
        lams = [X[i] for i in range(len(X)) if y[i] == c]
        features_for_class = list(filter(lambda f: str(f["properties"]["tmsNumber"]) in lams, feats))
        for f in features_for_class:
            f["properties"]["color"] = colors[i%(len(colors))]
            result_features.append(f)
        updated_features_for_main_source = list(filter(lambda f: str(f["properties"]["tmsNumber"]) not in lams, feats))
        print(f"Feats for class {c}: {len(features_for_class)}, feats left: {len(updated_features_for_main_source)}")
        feats = updated_features_for_main_source

    print(f"Found total of {len(result_features)}pcs of classified circles")
    print(f"Found total of {len(feats)}pcs of unclassified circles")
    for f in feats:
        f["properties"]["color"] = "grey"
        result_features.append(f)

    stations["features"] = feats + result_features
    print(f"Found total of {len(stations['features'])}pcs of circles")
    print()
    main_source = GeoJSONSource(stations, source_id='points1')

    paint = Paint(circle_radius=5, circle_color=['get', 'color'])
    circles = PointCircleLayer(main_source, paint=paint)
    click = ClickInteraction(circles, properties=['name', 'tmsNumber', 'roadStationId', 'geometry', 'Tien_suunta', 'VVAPAAS1', 'VVAPAAS2', 'direction1Municipality', 'direction2Municipality', 'coords'])
    # https://pypi.org/project/mapboxgl-notebook/
    
    mapbox_map = MapboxMap(
        access_token=access_token,
        style='mapbox://styles/mapbox/streets-v11',
        zoom=11,
        center=[22.186667, 60.491389],
        sources=[main_source],  # can be list of sources
        layers=[circles],  # can be list of layers
        interactions=[click],
    )
    return (mapbox_map, stations)

def create_mapbox_with_classifications_ints(X, y):
    classes = np.unique(y)

    # Must be a public token, starting with `pk`
    access_token = 'YOUR_TOKEN_HERE'

    stations = get_tms_stations(path="tms-stations.json", sensor_path="tms-sensor-constants.json")
    feats = stations["features"]
    lam_ids = []
    for s in stations["features"]:
        lam_ids.append(s["properties"]["tmsNumber"])

    result_features = []
    colors = ["blue", "green", "red", "yellow", "orange", "purple"]

    for i in range(len(classes)):
        c = classes[i]
        lams = [X[i] for i in range(len(X)) if y[i] == c]
        features_for_class = list(filter(lambda f: f["properties"]["tmsNumber"] in lams, feats))
        color = colors[i%(len(colors))]
        for f in features_for_class:
            f["properties"]["color"] = color
            result_features.append(f)
        updated_features_for_main_source = list(filter(lambda f: f["properties"]["tmsNumber"] not in lams, feats))
        print(f"Feats for class {c} ({color}): {len(features_for_class)}, feats left: {len(updated_features_for_main_source)}")
        feats = updated_features_for_main_source

    print(f"Found total of {len(result_features)}pcs of classified circles")
    print(f"Found total of {len(feats)}pcs of unclassified circles")
    for f in feats:
        f["properties"]["color"] = "grey"
        result_features.append(f)

    stations["features"] = feats + result_features
    print(f"Found total of {len(stations['features'])}pcs of circles")
    print()
    main_source = GeoJSONSource(stations, source_id='points1')

    paint = Paint(circle_radius=5, circle_color=['get', 'color'])
    circles = PointCircleLayer(main_source, paint=paint)
    click = ClickInteraction(circles, properties=['name', 'tmsNumber', 'roadStationId', 'geometry', 'Tien_suunta', 'VVAPAAS1', 'VVAPAAS2', 'direction1Municipality', 'direction2Municipality', 'coords'])
    # https://pypi.org/project/mapboxgl-notebook/
    
    mapbox_map = MapboxMap(
        access_token=access_token,
        style='mapbox://styles/mapbox/streets-v11',
        zoom=11,
        center=[22.186667, 60.491389],
        sources=[main_source],  # can be list of sources
        layers=[circles],  # can be list of layers
        interactions=[click],
    )
    return (mapbox_map, stations)

def create_mapbox_with_classifications_ints_with_direction(X, y, directions, move_amount = 0.005, verbose=0):
    classes = np.unique(y)
    directions = np.array(directions)
    X = np.array(X)

    # Must be a public token, starting with `pk`
    access_token = 'YOUR_TOKEN_HERE'

    stations = get_tms_stations(path="tms-stations.json", sensor_path="tms-sensor-constants.json")
    feats = stations["features"]
    updated_features_for_main_source = feats
    lam_ids = []
    for s in stations["features"]:
        lam_ids.append(s["properties"]["tmsNumber"])

    result_features = []
    colors = ["blue", "green", "red", "yellow", "orange", "purple"]

    verbose_strings = []

    for i in range(len(classes)):
        c = classes[i]
        lam_indices = [i for i in range(len(X)) if y[i] == c]
        lams = X[lam_indices]
        dirs = directions[lam_indices]
        features_for_class = list(filter(lambda f: f["properties"]["tmsNumber"] in lams, feats))
        color = colors[i%(len(colors))]
        for j in range(len(lams)):
            jth_lam_id = lams[j]
            direction = dirs[j]
            f = None
            for feat in features_for_class:
                if feat["properties"]["tmsNumber"] == jth_lam_id:
                    f = deepcopy(feat)
                    break
            if f == None:
                print("ERROR NONE")
                print(f"Cant find feature for lam id {jth_lam_id}")
                print(jth_lam_id in lam_ids)
            f["properties"]["color"] = color
            if direction == 2:
                # Pump the point 50m right
                f["geometry"]["coordinates"][0] += move_amount
            result_features.append(f)
        updated_features_for_main_source = list(filter(lambda f: f["properties"]["tmsNumber"] not in lams, updated_features_for_main_source))
        if verbose == 2:
            print(f"Feats for class {c+1} ({color}): {len(features_for_class)}, feats left: {len(updated_features_for_main_source)}")
        if verbose == 1:
            verbose_strings.append(f"Cluster {c+1} ({color}) {len(features_for_class)}pcs")
        #feats = updated_features_for_main_source

    if verbose == 2:
        print(f"Found total of {len(result_features)}pcs of classified circles")
        print(f"Found total of {len(feats)}pcs of unclassified circles")
        print(f"Found total of {len(stations['features'])}pcs of circles")
        print()
    if verbose == 1:
        print(" --- ".join(verbose_strings))
    for f in updated_features_for_main_source:
        f["properties"]["color"] = "grey"
        result_features.append(f)

    stations["features"] = feats + result_features
    main_source = GeoJSONSource(stations, source_id='points1')

    paint = Paint(circle_radius=5, circle_color=['get', 'color'])
    circles = PointCircleLayer(main_source, paint=paint)
    click = ClickInteraction(circles, properties=['name', 'tmsNumber', 'roadStationId', 'geometry', 'Tien_suunta', 'VVAPAAS1', 'VVAPAAS2', 'direction1Municipality', 'direction2Municipality', 'coords'])
    # https://pypi.org/project/mapboxgl-notebook/
    
    mapbox_map = MapboxMap(
        access_token=access_token,
        style='mapbox://styles/mapbox/streets-v11',
        zoom=11,
        center=[22.186667, 60.491389],
        sources=[main_source],  # can be list of sources
        layers=[circles],  # can be list of layers
        interactions=[click],
    )
    return (mapbox_map, stations)