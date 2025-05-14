
class Graph:
    def __init__(self):
        self.graph = []
        self.node_addresses = []

    def add_node(self, name, address):
        index = len(self.graph)
        self.node_addresses.append((name,address))
        self.graph.append([])  # Add a new empty list for the new node

    def add_edge(self, node1, node2, distance):
        max_index = max(node1, node2)
        while len(self.graph) <= max_index:
            self.add_node('','')  # Ensure nodes exist before adding an edge

        self.graph[node1].append((node2, distance))
        self.graph[node2].append((node1, distance))  # Because it's not a digraph

    def get_address(self, node_id):
        if 0 <= node_id < len(self.node_addresses):
            return self.node_addresses[node_id]
        return "Invalid Node ID"

    def remove_node(self, node):
        if node < len(self.graph):
            self.graph.pop(node)  # Remove the node
            for edges in self.graph:  # Remove all references to the deleted node
                while node in edges:
                    edges.remove(node)

    def get_node_index(self, address):
        for index, (name, node_address) in enumerate(self.node_addresses):
            # Extract just the street address part (before any parentheses or newlines)
            street_address = node_address.split('\n')[0] if '\n' in node_address else node_address
            street_address = street_address.split('(')[0] if '(' in street_address else street_address
            street_address = street_address.strip()

            # Compare with the provided address
            if street_address == address.strip():
                return index
        return None

    def display(self):
        for i, edges in enumerate(self.graph):
            name, address = self.node_addresses[i]
            print(f"{i}: {name} ({address}) -> {edges}")

    def get_route_distance(self, start_node, end_node):
        # Validate node indices
        if start_node is None or end_node is None:
            return float('inf')

        if start_node == end_node:
            return 0.0

        # Search for direct edge
        for neighbor, distance in self.graph[start_node]:
            if neighbor == end_node:
                return distance

        # Fallback: Find minimum distance through graph traversal
        visited = set()
        distances = {start_node: 0}
        unvisited = [(0, start_node)]

        while unvisited:
            current_distance, current_node = min(unvisited)
            unvisited.remove((current_distance, current_node))

            if current_node == end_node:
                return current_distance

            if current_node in visited:
                continue

            visited.add(current_node)

            for neighbor, edge_distance in self.graph[current_node]:
                if neighbor not in visited:
                    new_distance = current_distance + edge_distance

                    if neighbor not in distances or new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        unvisited.append((new_distance, neighbor))

        return float('inf')  # No route found
