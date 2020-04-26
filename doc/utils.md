# utils

[toc]

# utils.graph_parser

Carraretto Gabriel H.
graph_parser
Parses a given set of JSON OpenPose structured data in a cleaner and more easy-to-use JSON structured data


## parse_edges
```python
parse_edges(graph: dict, del_nodes: list, index: int, node_type: str)
```

Given a graph, a list of nodes to be deleted and the type of nodes(pose, hand or face), takes the edge set specified by node_type, removes the edges specified in del_nodes list, and return the resulting set of edges.
`graph`: Graph represented as a dict, containing only nodes
list `del_nodes`: Nodes to be deleted
int `index`: Index of the current person
str `node_type`: Type of nodes needed ('pose', 'hand' or 'face'). Default: 'pose'
:return list: List containing only the edges not specified in del_nodes


## parse_nodes
```python
parse_nodes(graph: dict, keypoints: list, index: int, k_type: str)
```

Given a graph represented as a dictionary, keypoints taken from a JSON, the index of the given graph, the type of keypoints(pose,handl, handr, face, parse the keypoints by creating nodes with the following attributes: {x, y, confidence}. Appends each node to the given graph.
dict `graph`: Graph represented as a dictionary
list `keypoints`: List of keypoints taken from OpenPose JSON
int `index`: Counter that represents the id of the current person keypoints being parsed
str `k_type`: Type of the given keypoints. Can be one of: 'pose', 'handl', 'handr' or 'face'
:return list: List of indexes of nodes for which no information was obtained by OpenPose


## find_node
```python
find_node(node_list: list, node_id: int)
```

Given a list of nodes and the id of a node, returns the given node if it exists, otherwise None
list `node_list`: List of nodes
int `node_id`: The id of a node
:return dict or None: The node with the given id, if it is found, otherwise None


## find_index
```python
find_index(node_list: list, node_id: int)
```

Given a list of nodes, and the id of a node, returns the position of the given node inside the list if it exists, otherwise None
list `node_list`: List of nodes
int `node_id`: The id of a node
:return int: Position of the node with the given id in the list, otherwise None


## generate_dataset
```python
generate_dataset(path)
```

Given a path to a folder containing JSON files generated by OpenPose, parse the files and generate a set of graphs based on the data set given, and save them as JSON in '../out/'
str `path`: path containing data generated by OpenPose


# utils.category_filter

Carraretto Gabriel H.
category_filter
Retrieves a set of filenames associated to a given category


## parse_category
```python
parse_category(cat_name: str, path='../mpii_human_pose/dataset.mat')
```

Given a category and a path, parses the elements inside a .mat file, in order to retrieve all the image file names that are within the given category
str `cat_name`: category of a given activity
str `path`: path to the .mat file
:return list: list of file names to be retrieved


# utils.edges_ref

Carraretto Gabriel H.
edges_ref
Contains all the OpenPose edge references for face, hands and pose


## get_edges
```python
get_edges(node_type: str)
```

Given a node type (pose, face, hand), returns the given edge set
str `node_type`: the type of nodes needed
:return list or None: list of edges, otherwise None


# utils.image_info

Carraretto Gabriel H.
image_info
Fetches the resolution values from a set of images, and save the info as txt files


## get_resolution
```python
get_resolution(path_name: str)
```

Given a path of a txt generated by generate_image_info, returns its content
str `path_name`: path of the txt file
:return str: resolution of an image specified by path_name


## generate_image_info
```python
generate_image_info(path: str)
```

Given a path, creates a folder for the output, if it doesn't exists, and saves on the output folder for each image a txt containing its resolution
str `path`: path of the images


# utils.networkx_converter

networkx_converter
Converts a JSON structured set of graphs, into an array of networkx graphs


## get_nx_graph
```python
get_nx_graph(path: str, node_type: str = 'pose')
```

Given a file path name, and the type of graph nodes, returns a list of networkx graphs
str `path`: path name of a given file
str `node_type`: type of graph nodes wanted. Can be one of: 'pose', 'handl', 'handr', 'face'
:return list or None: list containing a graph for each person in the file
