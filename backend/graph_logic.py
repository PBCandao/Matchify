import networkx as nx
from datetime import datetime

G = nx.Graph()

def add_user(user_id, **attrs):
    """
    Add a node for the given user_id with attributes.
    """
    G.add_node(user_id, **attrs)

def add_relationship(u1, u2, weight=1.0, status='connected'):
    """
    Add an undirected edge between u1 and u2 with weight, status,
    and record the lastInteraction timestamp.
    """
    last_interaction = datetime.utcnow().isoformat()
    G.add_edge(u1, u2,
               weight=weight,
               status=status,
               lastInteraction=last_interaction)

def get_graph(user_id: str, depth: int):
    """
    Perform a BFS from `user_id` out to `depth` hops and
    return (nodes, links) within that neighborhood.
    Nodes are returned as dicts with 'id' and node attributes.
    Links are returned as dicts with 'source', 'target', and edge attributes.
    """
    if user_id not in G:
        return [], []

    # Find all nodes within the given depth
    lengths = nx.single_source_shortest_path_length(G, user_id, cutoff=depth)
    nodes = []
    for node in lengths:
        attrs = dict(G.nodes[node])
        node_info = {'id': node}
        node_info.update(attrs)
        nodes.append(node_info)

    # Build links among the included nodes
    subgraph = G.subgraph(lengths.keys())
    links = []
    for u, v, data in subgraph.edges(data=True):
        link_info = {'source': u, 'target': v}
        link_info.update(data)
        links.append(link_info)

    return nodes, links
