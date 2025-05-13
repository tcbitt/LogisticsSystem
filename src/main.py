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

    for package in delayed_packages:
        truck3.add_package(package_table.search(package))
        package_table.remove(package)

    # Get the packages that are delayed until 9:05 AM
    for package in package_table.table:
        if package and package.value.notes.startswith("Delayed on flight"):
            delayed_packages.append(package.value.ID)

    for ea_truck in trucks:
        ea_truck.delivery_route = nearest_neighbor(g, ea_truck, package_table ,visited_hubs)

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
                            print(f"Truck {ea_truck.truck_id} delivered package {package.ID} at {current_time.strftime('%I:%M %p')}")
                        else:
                            continue
                    break
                else:
                    continue

    for ea_truck in trucks:
        undelivered = []
        for package in ea_truck.packages:
            if not hasattr(package, 'delivery_time') or not package.delivery_time:
                undelivered.append(package)
                print(f"Package {package.ID} was not delivered: Address: {package.address}")

        if undelivered:
            print(f"\nTruck {ea_truck.truck_id} has {len(undelivered)} undelivered packages:")
            for pkg in undelivered:
                # Try to add these to a special clean-up route
                node_idx = g.get_node_index(pkg.address)
                print(f"Package {pkg.ID}: Address: {pkg.address}, Node Index: {node_idx}")

    # FOR DEBUGGING-----------------------------------------------------------------
    unmatched_packages = []
    unmatched_routes = []
    for truck in trucks:
        # Check packages against routes
        for package in truck.packages[:]:  # Create a copy to safely modify
            package_match = any(
                g.get_node_index(package.address) == route_stop
                for route_stop in truck.delivery_route
            )
            if not package_match:
                unmatched_packages.append(package)
                truck.packages.remove(package)
        # Check routes against packages
        for route_stop in truck.delivery_route:
            route_has_package = any(
                g.get_node_index(package.address) == route_stop
                for package in truck.packages
            )

            if not route_has_package:
                unmatched_routes.append(route_stop)
    #--------------------------------------------------------------------------------
    for truck in trucks:
        # Check route against expected hub routes
        expected_hub_routes = set(
            g.get_node_index(package.address)
            for package in truck.packages
        )

        # Compare expected hub routes with actual truck routes
        routes_without_packages = [
            route for route in truck.delivery_route
            if route not in expected_hub_routes
        ]

        # If there are unexpected routes, log or handle them
        if routes_without_packages:
            print(f"Truck {truck.truck_id} has routes without packages: {routes_without_packages}")
            # Optionally: remove these routes or take corrective action

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

def get_package_data(trucks, time, delayed_packages):
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

def nearest_neighbor(graph, truck, packages, visited):
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