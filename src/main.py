import csv
import re
from datetime import timedelta
from datetime import datetime
from modules import Package
from modules import HashTable
from modules import Truck
from modules import Graph


def main():
    truck1 = Truck(1)
    truck2 = Truck(2)
    truck3 = Truck(3)

    trucks = [truck1, truck2, truck3]

    truck1_departure_time = datetime.strptime("8:00 AM", "%I:%M %p").time()
    truck2_departure_time = datetime.strptime("9:05 AM", "%I:%M %p").time()
    truck3_departure_time = datetime.strptime("10:30 AM", "%I:%M %p").time()

    distance_file_path = "./resources/distances.csv"
    package_file_path = "./resources/packages.csv"

    # Graph instantiation.
    g = Graph()
    load_graph_from_csv(g, distance_file_path)
    #g.display()

    # Instantiate the hashtable using the package_file.
    package_table = HashTable()
    reference_table = HashTable()

    # Populate the hash table using the get_packages method.
    get_packages(package_table, package_file_path)
    get_packages(reference_table, package_file_path)


    visited_hubs = set()
    packages_delivered_together = []
    delayed_packages = []

    # Get the truck 2 packages
    for package in package_table.table:
        if package and package.value.notes == "Can only be on truck 2":
            truck2.add_package(package.value)
            package_table.remove(package.key)

    # Get the packages that need to be delivered together
    for package in package_table.table:
        if package and package.value.notes.startswith("Must be delivered"):
            packages_delivered_together.append(package.value.ID)
            package_id_regex = re.findall(r'\d+', package.value.notes)
            for package_id in package_id_regex:
                package_id = int(package_id)  # Convert to integer
                if package_id not in packages_delivered_together:  # Avoid duplicates
                    packages_delivered_together.append(package_id)

    for package in packages_delivered_together:
        truck1.add_package(package_table.search(package))
        package_table.remove(package)

    for package in delayed_packages:
        truck3.add_package(package_table.search(package))
        package_table.remove(package)

    # Get the packages that are delayed until 9:05 AM
    for package in package_table.table:
        if package and package.value.notes.startswith("Delayed on flight"):
            delayed_packages.append(package.value.ID)

    for ea_truck in trucks:
        ea_truck.delivery_route = nearest_neighbor(g, ea_truck, package_table ,visited_hubs, packages_delivered_together, delayed_packages)

    # Load remaining packages onto the last truck
    for package in package_table.table:
        for ea_truck in trucks:
            if len(ea_truck.packages) < 16:
                if package:
                    truck3.add_package(package.value)
                    package_table.remove(package)

    for ea_truck in trucks:
        first_priority_list = []
        second_priority_list = []
        # Always load from the hub
        current_hub = 0
        for package in ea_truck.packages:
            if package:
                if package.deadline == "9:00 AM":
                    first_priority_list.append(g.get_node_index(package.address))
                elif package.deadline == "10:30 AM":
                    second_priority_list.append(g.get_node_index(package.address))

        edge_list = []
        seen = set()
        path_list = [x for x in (first_priority_list + second_priority_list) if not (x in seen or seen.add(x))]
        route = [0]
        for i in path_list:
            route.append(i)

        for i in ea_truck.delivery_route:
            if i in path_list:
                continue
            else:
                path_list.append(i)

        if 0 in path_list:
            path_list.remove(0)
            path_list.insert(0, 0)

        ea_truck.delivery_route = path_list

    for ea_truck in trucks:
        print("\n\n")
        current_time = ea_truck.departure_time
        # Set the package status to en route
        for package in ea_truck.packages:
            package.status = "En route"
        for i in range(len(ea_truck.delivery_route) - 1):
            hub = ea_truck.delivery_route[i]
            next_hub_idx = ea_truck.delivery_route[i + 1]
            edges = g.graph[hub]
            for edge in edges:
                if edge[0] == next_hub_idx:
                    time_taken = (edge[1] / 18) * 60
                    current_time += timedelta(minutes=time_taken)
                    for package in ea_truck.packages:
                        idx = g.get_node_index(package.address)
                        if g.get_node_index(package.address) == next_hub_idx:
                            package.status = "Delivered"
                            package.delivery_time = current_time.strftime("%I:%M %p")
                            print(
                                f"Truck {ea_truck.truck_id} delivered package {package.ID} at {current_time.strftime('%I:%M %p')}")
                            break
                        else:
                            continue
                    break
                else:
                    continue

    print(f"Total mileage: {sum(obj.mileage for obj in trucks)} miles")



    print("STOP")

# Get the packages from the package file.
def get_packages(packages_hash_table, package_file):
    with open(package_file, 'r') as file:
        # Skip the header row
        package_data = csv.reader(file)
        next(package_data)  # Skip header row

        for row in package_data:
            pkg_id = int(row[0])
            address = row[1]
            city = row[2]
            state = row[3]
            zip_code = row[4]
            deadline = row[5]
            weight_kg = int(row[6])
            notes = row[7]

            # Create package object with initial status "at hub"
            package = Package(pkg_id, address, city, state, zip_code,
                              deadline, weight_kg, notes, "At Hub")

            # Insert package into hash table
            packages_hash_table.insert(pkg_id, package)

def nearest_neighbor(graph, truck, packages, visited, packages_delivered_together, delayed_packages):
    # Start at HUB
    current_hub_index = 0
    visited.add(current_hub_index)
    truck.delivery_route.append(current_hub_index)

    while len(visited) < len(graph.graph) and len(truck.packages) < 16:
        # Find the closest unvisited neighbor from current hub
        smallest_edge = float('inf')
        next_hub = None

        for neighbor, distance in graph.graph[current_hub_index]:
            if neighbor not in visited and distance < smallest_edge:
                smallest_edge = distance
                next_hub = neighbor

        # If no unvisited neighbor found
        if next_hub is None:
            break

        # Move to the next hub
        current_hub_index = next_hub
        truck.mileage += graph.graph[current_hub_index][0][1]
        visited.add(current_hub_index)
        truck.delivery_route.append(current_hub_index)

        # Check if any packages need to be delivered to this hub
        hub_address = graph.node_addresses[current_hub_index][1].split('\n')[0].strip()

        for bucket in packages.table:
            current = bucket
            if current:
                # Compare package address with current hub address
                if current.value.address == hub_address and len(truck.packages) < 16:
                    if current:
                        if current.value.deadline != "EOD" and truck.truck_id == 3:
                            break
                        else:
                            truck.add_package(current.value)
                            packages.remove(current.key)
                            print(f"Added package #{current.value.ID} to truck {truck.truck_id}")

    return truck.delivery_route


def load_graph_from_csv(graph, csv_filename):
    with open(csv_filename, newline='') as file:
        reader = csv.reader(file)

        distance_matrix = []
        locations = []

        for row in reader:
            # Extract location name & address
            name, address = row[:2]
            # Store node information
            locations.append((name.strip('"'), address.strip('"')))
            # Convert to float, allow None
            distances = [float(cell) if cell.strip() else None for cell in row[2:]]

            distance_matrix.append(distances)

        # Add nodes
        for name, address in locations:
            graph.add_node(name, address)

        # Extract lower triangle matrix properly
        for i in range(len(distance_matrix)):
            # Lower triangle extraction
            for j in range(i):
                if distance_matrix[i][j] is not None:
                    graph.add_edge(i, j, distance_matrix[i][j])

    return graph


if __name__ == "__main__":
    main()