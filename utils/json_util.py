import json


def loadjson(filename):
    with open(filename, encoding='utf-8', mode="r") as f:
        return json.loads(f.read())

def savejson(filename, data):
    with open(filename, encoding='utf-8', mode="w") as f:
        json.dump(data, f, indent=4, ensure_ascii=True)
