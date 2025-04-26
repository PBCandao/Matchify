import networkx as nx
from datetime import datetime
import notifications
import db

G = nx.Graph()

def add_user(user_id, **attrs):
    """
    Add a node for the given user_id with attributes.
    """
    G.add_node(user_id, **attrs)
    # Notification hooks for new user
    event = {
        'type': 'new_user',
        'user': user_id,
        'attrs': attrs,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        notifications.log_event(user_id, event['type'], event)
        notifications.emit_notification(user_id, event)
    except Exception:
        pass
    # Broadcast new node event
    try:
        node_info = {'id': user_id}
        node_info.update(attrs)
        notifications.broadcast_graph_update('new_node', node_info)
    except Exception:
        pass

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
    # Notification hooks for new relationship
    event = {
        'type': 'new_relationship',
        'from': u1,
        'to': u2,
        'weight': weight,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        notifications.log_event(u1, event['type'], event)
        notifications.log_event(u2, event['type'], event)
        notifications.emit_notification(u1, event)
        notifications.emit_notification(u2, event)
    except Exception:
        pass
    # Broadcast new link event
    try:
        link_info = {
            'source': u1,
            'target': u2,
            'weight': weight,
            'status': status,
            'lastInteraction': last_interaction
        }
        notifications.broadcast_graph_update('new_link', link_info)
    except Exception:
        pass

def get_graph(user_id: str, depth: int):
    """
    Perform a BFS from `user_id` out to `depth` hops and
    return (nodes, links) within that neighborhood.
    Nodes are returned as dicts with 'id' and node attributes.
    Links are returned as dicts with 'source', 'target', and edge attributes.
    """
    if user_id not in G:
        return [], []

    # Find all nodes within the given depth (depth=0 for user itself)
    lengths = nx.single_source_shortest_path_length(G, user_id, cutoff=depth)
    nodes = []
    for node, dist in lengths.items():
        attrs = dict(G.nodes[node])
        # Include depth in node info
        node_info = {'id': node, 'depth': dist}
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
 
def load_data_from_db():
    """
    Load all users and relationships from the SQLite database into the in-memory graph.
    """
    # Clear existing in-memory graph
    G.clear()
    # Load users
    for u in db.get_all_users():
        uid = u.pop('id')
        roles = u.pop('roles', [])
        G.add_node(uid, **u, roles=roles)
    # Load relationships
    for r in db.get_all_relationships():
        u1 = r['user1_id']
        u2 = r['user2_id']
        weight = r.get('weight', 1.0)
        status = r.get('status', 'connected')
        last = r.get('lastInteraction')
        # Undirected graph will merge duplicates
        G.add_edge(u1, u2, weight=weight, status=status, lastInteraction=last)
    
def get_path(u1, u2):
    """
    Return the shortest path (list of user IDs) between u1 and u2, or empty list if no path.
    """
    try:
        return nx.shortest_path(G, u1, u2)
    except Exception:
        return []
