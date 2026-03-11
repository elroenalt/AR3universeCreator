import json
import os
def getdimensionProperties(dP_path = 'dimensionProperties'):
    dimensionProperties = []
    dP_names = os.listdir(dP_path)
    for path in dP_names:
        file = open(os.path.join(dP_path,path))
        json_con = json.load(file)
        file.close()
        path = path.removesuffix(".json")
        dimensionProperties.append((json_con,path))
    return dimensionProperties

getdimensionProperties()
