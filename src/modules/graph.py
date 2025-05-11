
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

