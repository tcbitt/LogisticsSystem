import pandas as pd
import networkx as nx
import re
from matplotlib import pyplot as plt
from modules import Package
from modules import HashTable
from modules import Truck

def main():
    truck1 = Truck(1)
    truck2 = Truck(2)
    truck3 = Truck(3)

    trucks = [truck1, truck2, truck3]

    # Get the packages from the package file.
    package_file_path = "./resources/WGUPS Package File.xlsx"
    pf = pd.read_excel(package_file_path, sheet_name='Sheet1', header=7,
                       dtype={'Package ID': int,
                              'Address': str,
                              'City': str,
                              'State': str,
                              'Zip': str,
                              'Delivery Deadline': str,
                              'Weight KILO': int,
                              'Special Notes': str
                              },
                       keep_default_na=False
                       )

    # Get the distances from the distance table.
    distance_file_path = "./resources/WGUPS Distance Table.xlsx"
    df = pd.read_excel(distance_file_path, sheet_name="Sheet1", header=None)

    # Graph instantiation.
    g = nx.Graph()

    # Populate graph g with the distance information and a visited attribute.
    get_distances(df, g)
    visited_dict = {node: False for node in g.nodes()}
    nx.set_node_attributes(g, visited_dict, "visited")

    # Instantiate the hashtable using the package_file.
    packages = HashTable()

    # Populate the hash table using the get_packages method.
    get_packages(pf, packages)

    print("Edges in Graph:")
    for edge in g.edges(data=True, ):
        node1, node2, data = edge
        visited = g.nodes[node2]["visited"]
        print(f"{edge}, visited: ({visited})")

    ''''# Print the hashtable to ensure its populating correctly.
    for bucket in packages.table:
        current = bucket
        while current:
            print(f"KEY:{current.key}\nPACKAGE: {current.value}")
            current = current.next'''

    visited_hubs = set()

    for ea_truck in trucks:
        ea_truck.delivery_route = nearest_neighbor(g, ea_truck, packages, "Western Governors University\n4001 South 700 East, \nSalt Lake City, UT 84107", visited_hubs)
        print(f"Truck {ea_truck.truck_id} route: {ea_truck.delivery_route}")


    print("BREAK POINT!")


# Method to plot the graph for visual inspection, so I can ensure the graph looks correct and has the correct number of edges.
def plot_graph(graph):
    plt.figure(figsize=(50, 50))
    nx.draw(graph, with_labels=True)
    plt.show()

# Method to read the package
def get_packages(package_file, packages):
    # Read through the package file and create a list of Packages to be added to the hashtable, also get the size iterating through the rows for the hashtable.
    for _, row in package_file.iterrows():
        package_id = row['Package ID']  # Replace with actual column name if needed
        package = Package(
            package_id,
            row['Address'],
            row['City'],
            row['State'],
            row['Zip'],
            row['Delivery Deadline'],
            row['Weight KILO'],
            row['Special Notes'],
            "At the hub"
        )
        packages.insert(package_id, package)


def get_distances(distance_file, graph):
    # Extract hub names & addresses (Rows 8-34, Columns 0 & 1).
    hub_names = distance_file.iloc[8:35, 0].dropna().tolist()
    hub_addresses = distance_file.iloc[8:35, 1].dropna().tolist()

    # Create a dictionary mapping hubs to addresses.
    hub_info = {hub_names[i]: hub_addresses[i] for i in range(len(hub_names))}

    # Add hubs as nodes with their addresses
    for hub, address in hub_info.items():
        graph.add_node(hub, address=address)

    # Add weighted edges based on the lower half of the matrix.
    for i in range(8, 35):  # Rows 8-34 contain distances
        source_hub = distance_file.iloc[i, 0]  # Column 0 is the hub names.
        for j in range(i - 7):  # Extract only lower triangle values.
            target_hub = hub_names[j]
            distance = distance_file.iloc[i, j + 2]

            if pd.notna(distance):
                graph.add_edge(source_hub, target_hub, weight=float(distance))
                graph.add_edge(target_hub, source_hub, weight=float(distance))  # Mirror for full adjacency.


def nearest_neighbor(graph, truck, packages, start_hub, visited):
    current_hub = start_hub

    while len(truck.packages) < 16:
        visited.add(current_hub)
        print("Truck Number:", truck.truck_id)
        truck.delivery_route.append(current_hub)

        # Find the nearest unvisited hub
        next_hub = None
        min_distance = float('inf')
        pattern = re.compile('^[^\n]+\n([^\n,]+)')

        for bucket in packages.table:
            if current_hub == 'Western Governors University\n4001 South 700 East, \nSalt Lake City, UT 84107':
                break
            current = bucket
            while current:
                match = pattern.match(current_hub).group(1).strip()
                if current.value.address == match:
                    truck.add_package(current.value)
                    packages.remove(current.key)

                current = current.next

        for neighbor in graph.neighbors(current_hub):
            if neighbor not in visited:
                distance = graph[current_hub][neighbor]['weight']
                if distance < min_distance:
                    min_distance = distance
                    next_hub = neighbor

        if next_hub:
            current_hub = next_hub
            truck.mileage += min_distance
            visited.add(next_hub)

            # Load packages onto the truck
            for bucket in packages.table:
                current = bucket
                while current:
                    if current.value.address == graph.nodes[next_hub]['address']:
                        truck.add_package(current.value)
                    current = current.next
        else:
            break  # No more unvisited hubs



    return truck.delivery_route




if __name__ == "__main__":
    main()

