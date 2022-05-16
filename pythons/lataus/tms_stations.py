import json

with open('./tms-stations.json') as f:
  data = json.load(f)

ely_codes = ['01', '02', '03', '04', '08', '09', '10', '12', '14']

def create_station_dictionary(json_data, ely_codes):
    result = dict()
    
    for code in ely_codes:
        tms_numbers = []
        for tms in data['features']:
            if tms['properties']['provinceCode'] == str(int(code)):
                tms_numbers.append(tms['properties']['tmsNumber'])
        result[code] = tms_numbers
                
    return result

print(create_station_dictionary(data, ely_codes))