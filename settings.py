import json
 
def get_settings():
    # Opening JSON file
    with open('settings.json') as json_file:
        data = json.load(json_file)
    return data