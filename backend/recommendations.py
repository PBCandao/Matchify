#!/usr/bin/env python3
"""
Friend-of-friend and role-based recommendation algorithms.
"""
import networkx as nx

import graph_logic

def get_suggestions(user_id: str):
    """
    Return a list of recommendation dicts for `user_id`, combining:
      - mutual friend counts (FoF)
      - shared role boosts within 2 hops
    Each suggestion contains: id, mutual_friends, role_match, score.
    """
    G = graph_logic.G
    if user_id not in G:
        return []

    # BFS to depth 2
    lengths = nx.single_source_shortest_path_length(G, user_id, cutoff=2)
    nodes_within = set(lengths.keys())
    # direct neighbors
    direct_neighbors = set(nx.neighbors(G, user_id))
    # roles of the user
    user_roles = set(G.nodes[user_id].get('roles') or [])

    suggestions = []
    for node in nodes_within:
        if node == user_id or node in direct_neighbors:
            continue

        # Friend-of-friend score: number of mutual direct neighbors
        neighbors_of_node = set(nx.neighbors(G, node))
        mutual_count = len(neighbors_of_node & direct_neighbors)

        # Role-based boost: count shared roles
        candidate_roles = set(G.nodes[node].get('roles') or [])
        role_match = len(candidate_roles & user_roles)

        # Combined score
        score = mutual_count + role_match
        suggestions.append({
            'id': node,
            'mutual_friends': mutual_count,
            'role_match': role_match,
            'score': score
        })

    # Sort by descending score, then by id
    suggestions.sort(key=lambda x: (-x['score'], x['id']))
    return suggestions
