import csv
import re
from _ast import If
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

    truck1.departure_time = datetime.strptime("8:00 AM", "%I:%M %p")
    truck2.departure_time = datetime.strptime("9:05 AM", "%I:%M %p")
    truck3.departure_time = datetime.strptime("10:45 AM", "%I:%M %p")

    distance_file_path = "./resources/distances.csv"
    package_file_path = "./resources/packages.csv"

    # Graph instantiation.
    g = Graph()
    load_graph_from_csv(g, distance_file_path)

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
                # Convert to integer
                package_id = int(package_id)
                if package_id not in packages_delivered_together:
                    # Avoid duplicates
                    packages_delivered_together.append(package_id)

    for package in packages_delivered_together:
        truck1.add_package(package_table.search(package))
        package_table.remove(package)

        # Get the packages that are delayed until 9:05 AM
    for package in package_table.table:
        if package and package.value.notes.startswith("Delayed on flight"):
            delayed_packages.append(package.value.ID)

    for package in delayed_packages:
        truck3.add_package(package_table.search(package))
        package_table.remove(package)

    for ea_truck in trucks:
        ea_truck.delivery_route = nearest_neighbor(g, ea_truck, package_table , visited_hubs)


    for ea_truck in trucks:
        first_priority_list = []
        second_priority_list = []
        for package in ea_truck.packages:
            if package:
                if package.deadline == "9:00 AM":
                    first_priority_list.append(g.get_node_index(package.address))
                elif package.deadline == "10:30 AM":
                    second_priority_list.append(g.get_node_index(package.address))
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
                        if g.get_node_index(package.address) == next_hub_idx:
                            package.status = "Delivered"
                            package.delivery_time = current_time.strftime("%I:%M %p")
                    break
                else:
                    continue

    while True:
        choice = menu()
        if choice == "1":
            time_input = input("Enter time (HH:MM AM/PM): ")
            try:
                # Parse the input time
                check_time = datetime.strptime(time_input, "%I:%M %p")
                check_package_status(trucks, check_time)
            except ValueError:
                print("Invalid time format. Please use HH:MM AM/PM format (e.g., 10:30 AM).")

        elif choice == "2":
            print(f"Total mileage: {sum(obj.mileage for obj in trucks)} miles")
        elif choice == "3":
            exit()
        else:
            continue

def menu():
    print("\n===== WGUPS Package Delivery System =====")
    print("1. View Package Status")
    print("2. View Total Mileage")
    print("3. Exit")
    return input("Enter your choice (1-3): ")

def get_package_data(trucks, time):
    for truck in trucks:
        print(f"Truck 1 packages at {time}")
        for package in truck.packages:
            if package.ID == 1:
                print(f"Package {package.ID} at {package.address} at {time}")

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

'''def nearest_neighbor(graph, truck, packages, visited, current_hub_index = 0):
    # Start at HUB
    visited.add(current_hub_index)
    truck.delivery_route.append(current_hub_index)
    while len(visited) < len(graph.graph):
        # Find the closest unvisited neighbor from current hub
        truck.mileage += graph.graph[current_hub_index][0][1]
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
        visited.add(current_hub_index)

    for hub in truck.delivery_route:
        if hub == 0:
            continue
        for package in packages.table:
            if package and hub == graph.get_node_index(package.value.address):
                if len(truck.packages) == 16:
                    break
                else:
                    truck.add_package(package.value)
                    packages.remove(package.key)

    return truck.delivery_route'''

def nearest_neighbor(graph, truck, packages, visited, current_hub_index=0):
    # Make a copy of the visited set to avoid affecting other trucks
    local_visited = visited.copy()

    # Start at HUB
    local_visited.add(current_hub_index)
    truck.delivery_route.append(current_hub_index)

    while len(local_visited) < len(graph.graph) and len(truck.packages) < 16:
        smallest_edge = float('inf')
        next_hub = None

        for neighbor, distance in graph.graph[current_hub_index]:
            if neighbor not in local_visited and distance < smallest_edge:
                smallest_edge = distance
                next_hub = neighbor

        # If no unvisited neighbor found
        if next_hub is None:
            break

        # Move to the next hub
        current_hub_index = next_hub
        local_visited.add(current_hub_index)

        # Add the mileage and add the hub to the route
        truck.mileage += smallest_edge
        truck.delivery_route.append(current_hub_index)

        # Try to add packages for this location right away
        for package in packages.table:
            if package and current_hub_index == graph.get_node_index(package.value.address):
                if len(truck.packages) < 16:  # Check capacity
                    truck.add_package(package.value)
                    packages.remove(package.key)

    # Update the shared visited set with locations this truck has visited
    visited.update(local_visited)

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

def check_package_status(trucks, check_time):
    print(f"\n--- Package Status Report at {check_time.strftime('%I:%M %p')} ---\n")

    # For each truck, display its packages and their status
    for truck in trucks:
        print(f"\nTruck {truck.truck_id} Packages:")
        print("-" * 90)
        print(f"{'ID':<5} {'Address':<40} {'Deadline':<12} {'Status':<12} {'Delivery Time':<12}")
        print("-" * 90)

        for package in truck.packages:
            # Determine package status based on time
            status = "At hub"
            delivery_time_str = "N/A"

            # If check time is before truck departure, package is at hub
            if check_time < truck.departure_time:
                status = "At hub"
            # If package has been delivered (has a delivery_time attribute)
            elif hasattr(package, 'delivery_time') and package.delivery_time:
                # Convert delivery_time string to datetime object for comparison
                try:
                    pkg_delivery_time = datetime.strptime(package.delivery_time, "%I:%M %p")
                    # If current time is after delivery time, package is delivered
                    if check_time >= pkg_delivery_time:
                        status = "Delivered"
                        delivery_time_str = package.delivery_time
                    else:
                        # Package is en route if truck has departed but not yet delivered
                        status = "En route"
                except (ValueError, TypeError):
                    # Handle any conversion errors
                    status = "En route"
            else:
                # If truck has departed but package has no delivery time
                if check_time >= truck.departure_time:
                    status = "En route"


            print(f"{package.ID:<5} {package.address:<40} {package.deadline:<12} {status:<12} {delivery_time_str:<12}")

        print("-" * 90)

if __name__ == "__main__":
    main()