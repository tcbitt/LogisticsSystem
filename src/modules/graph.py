class Graph:
    def __init__(self):
        self.graph = []

    def add_node(self):
        self.graph.append([])  # Add a new empty list for the new node

    def add_edge(self, node1, node2):
        max_index = max(node1, node2)
        while len(self.graph) <= max_index:
            self.add_node()  # Ensure nodes exist before adding an edge

        self.graph[node1].append(node2)
        self.graph[node2].append(node1)  # Because it's not a digraph

    def remove_node(self, node):
        if node < len(self.graph):
            self.graph.pop(node)  # Remove the node
            for edges in self.graph:  # Remove all references to the deleted node
                while node in edges:
                    edges.remove(node)

    def display(self):
        for i, edges in enumerate(self.graph):
            print(f"{i}: {edges}")
