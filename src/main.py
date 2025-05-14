import csv
import re
from _ast import If
from datetime import timedelta
from datetime import datetime

from sympy.codegen.ast import continue_

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
    truck3.departure_time = datetime.strptime("10:20 AM", "%I:%M %p")

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

    # [0] = grouped packages
    # [1] = late packages
    # [2] = truck 2 packages
    # [3] = all other packages
    package_id_buckets = get_constrained_packages(package_table)
    package_id_list = package_id_buckets[3]

    for ea_truck in trucks:
        load_packages(ea_truck, package_id_buckets, package_table)
        optimized_route = optimize_route(ea_truck, g, visited_hubs)
        ea_truck.delivery_route = optimized_route


    for ea_truck in trucks:
        ea_truck.delivery_route = nearest_neighbor(g, ea_truck, package_table , visited_hubs, package_id_list)



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

def optimize_route(truck, graph, visited, current_hub_idx=0):
    optimized_route = []
    visited.add(current_hub_idx)
    optimized_route.append(current_hub_idx)

    while len(visited) < len(truck.packages) + 1:
        shortest_edge = float('inf')
        next_hub = None

        for package in truck.packages:
            package_hub_idx = graph.get_node_index(package.address)
            if package_hub_idx not in visited:
                distance = graph.get_route_distance(current_hub_idx, package_hub_idx)
                if distance < shortest_edge:
                    shortest_edge = distance
                    next_hub = package_hub_idx

        if next_hub is None:
            break

        current_hub_idx = next_hub
        visited.add(current_hub_idx)
        optimized_route.append(current_hub_idx)

    return optimized_route


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
        # Skip header row
        next(package_data)

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

def nearest_neighbor(graph, truck, packages, visited, package_id_list, current_hub_index = 0):

    return
'''def nearest_neighbor(graph, truck, packages, visited, package_id_list, current_hub_index = 0):
    # Start at HUB
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
        visited.add(current_hub_index)
        truck.delivery_route.append(current_hub_index)
        truck.mileage += smallest_edge

        # Load the packages for this hub
        for package in packages.table:
            if package and current_hub_index == graph.get_node_index(package.value.address):
                if len(truck.packages) < 16:
                    truck.add_package(package.value)
                    packages.remove(package.key)

    return truck.delivery_route'''





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
                    if check_time >= pkg_delivery_time:
                        status = "Delivered"
                        delivery_time_str = package.delivery_time
                    else:
                        status = "En route"
                except (ValueError, TypeError):
                    status = "En route"
            else:
                # If truck has departed but package has no delivery time
                if check_time >= truck.departure_time:
                    status = "En route"

            print(f"{package.ID:<5} {package.address:<40} {package.deadline:<12} {status:<12} {delivery_time_str:<12}")

        print("-" * 90)

def get_constrained_packages(packages):
    grouped_packages = []
    late_packages = []
    truck2_packages = []
    all_other_packages = []

    for package in packages.table:
        if package:
            if package.value.ID in grouped_packages or package.value.ID in truck2_packages or package.value.ID in late_packages:
                continue
            elif "Must be delivered with" in package.value.notes:
                grouped_packages.append(package.value.ID)
                package_id_regex = re.findall(r'\d+', package.value.notes)
                for package_id in package_id_regex:
                    # Convert to integer
                    package_id = int(package_id)
                    if package_id not in grouped_packages:
                        # Avoid duplicates
                        grouped_packages.append(package_id)

            elif "Can only be on truck 2" in package.value.notes:
                truck2_packages.append(package.value.ID)

            elif "Delayed on flight" in package.value.notes:
                late_packages.append(package.value.ID)

            elif "Wrong address listed" in package.value.notes:
                late_packages.append(package.value.ID)

            else:
                if package.value.ID not in grouped_packages:
                    all_other_packages.append(package.value.ID)

    # Remove any duplicates that may appear
    for package in all_other_packages:
        if package in grouped_packages or package in late_packages or package in truck2_packages:
            all_other_packages.remove(package)

    package_buckets = [grouped_packages, late_packages, truck2_packages, all_other_packages]
    return package_buckets


def prioritize_packages(trucks, graph):
    for ea_truck in trucks:
        first_priority_list = []
        second_priority_list = []
        for package in ea_truck.packages:
            if package:
                if package.deadline == "9:00 AM":
                    first_priority_list.append(graph.get_node_index(package.address))
                elif package.deadline == "10:30 AM":
                    second_priority_list.append(graph.get_node_index(package.address))
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

        ea_truck.delivery_route.insert(0, path_list)

def deliver_packages(trucks, graph):
    for ea_truck in trucks:
        print("\n\n")
        current_time = ea_truck.departure_time
        # Set the package status to en route
        for package in ea_truck.packages:
            package.status = "En route"
        # Iterate through every hub on the trucks route
        for i in range(len(ea_truck.delivery_route) - 1):
            hub = ea_truck.delivery_route[i]
            next_hub_idx = ea_truck.delivery_route[i + 1]
            edges = graph.graph[hub]
            # Iterate through the edges to get the distance
            for edge in edges:
                if edge[0] == next_hub_idx:
                    time_taken = (edge[1] / 18) * 60
                    current_time += timedelta(minutes=time_taken)
                    for package in ea_truck.packages:
                        if graph.get_node_index(package.address) == next_hub_idx:
                            package.status = "Delivered"
                            package.delivery_time = current_time.strftime("%I:%M %p")
                    break
                else:
                    continue

def load_packages(truck, package_buckets, packages):
    # Add the grouped packages to either truck.
    if truck.truck_id != 3:
        if len(package_buckets[0]) <= 16 - len(truck.packages):
            for package in package_buckets[0][:]:
                if package:
                    if package not in truck.packages:
                        truck.add_package(packages.search(package))
                        package_buckets[0].remove(package)
                        packages.remove(package)
    # Add the packages to truck 2
    if truck.truck_id == 2:
        for package in package_buckets[2][:]:
            if len(truck.packages) < 16:
                truck.add_package(packages.search(package))
                package_buckets[2].remove(package)
                packages.remove(package)
            else:
                break

    # Add late packages to truck 3 as truck 1 and 2 leave earlier
    if truck.truck_id == 3:
        for package in package_buckets[1][:]:
            if len(truck.packages) < 16:
                truck.add_package(packages.search(package))
                package_buckets[1].remove(package)
                packages.remove(package)
            else:
                break


if __name__ == "__main__":
    main()