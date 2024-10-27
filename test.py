import json
with open("./graph.json", "r") as f:
    data = json.load(f)

location_dict = {}
for node in data:
    id = node["data"]["id"]
    position = node["position"]
    location_dict[id] = position

print(location_dict)

# save dict to json
with open('location.json', 'w') as f:
    json.dump(location_dict, f)