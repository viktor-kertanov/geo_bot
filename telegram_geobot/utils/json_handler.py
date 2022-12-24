import json

def save_data_as_json(data, filename):
    with open(filename, 'w', encoding='UTF-8') as f:
        data_json = json.dumps(data, indent=4, ensure_ascii=False)
        f.write(data_json)