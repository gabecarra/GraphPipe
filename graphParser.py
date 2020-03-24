import json
import sys
import os
import matplotlib.pyplot as plt
import networkx as nx

root_path = sys.argv[1] + '/'
out_path = root_path + '/out/'
G = nx.Graph()
EDGES = [(0, 1), (0, 15), (0, 16), (1, 2), (1, 5), (1, 8), (2, 3), (3, 4), (5, 6), (6, 7), (8, 9), (8, 12), (9, 10),
         (10, 11), (10, 11), (11, 22), (11, 24), (12, 13), (13, 14), (14, 19), (14, 21), (15, 17),(16, 18), (19, 20),
         (22, 23)]

try:
    os.mkdir(out_path)
except FileExistsError:
    print(out_path + " already exists...")
    pass


for root, dirs, files in os.walk(root_path):
    for file in files:
        print(file)
        if file.endswith('.json'):
            with open(root_path + file) as json_file:
                data = json.load(json_file)
                person_index = 0
                out_string = {'people': []}
                for person in data['people']:
                    pose_keypoints = person['pose_keypoints_2d']
                    null_nodes = []
                    for i in range(0, 75, 3):
                        x = pose_keypoints[i]
                        y = pose_keypoints[i + 1]
                        confidence = pose_keypoints[i + 2]
                        index = int(i / 3)
                        if x != 0 or y != 0:
                            G.add_node(index, x=x, y=y, confidence=confidence)
                        else:
                            null_nodes.append(index)
                    G.add_edges_from(EDGES)
                    for node in null_nodes:
                        G.remove_node(node)
                    out_string['people'].append({'id': person_index, 'value': nx.adjacency_data(G)})
                    person_index += 1
            with open(out_path + file, 'w') as out_file:
                json.dump(out_string, out_file, indent=2)
                G.clear()
    break

# nx.draw(G, with_labels='true', font_color='white', font_weight='bold')
# plt.show()
