import json
import os
# us load to json to py and dump for py to json
dimensionProperties = []
paths_dimensionProperties = os.listdir("dimensionProperties")
for path in paths_dimensionProperties:
    file = open(f'dimensionProperties\{path}')
    json_con = json.load(file)
    file.close()
    dimensionProperties.append(json_con)
print(dimensionProperties[0])