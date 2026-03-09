import json
import os

def getdimensionProperties(dP_path = 'dimensionProperties'):
    dimensionProperties = []
    dP_names = os.listdir(dP_path)
    for path in dP_names:
        file = open(os.path.join(dP_path,path))
        json_con = json.load(file)
        file.close()
        dimensionProperties.append({'name':path.strip(".json"),"content":json_con})
    return dimensionProperties


