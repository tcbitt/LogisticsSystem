from datetime import datetime

class Truck:
    def __init__(self, truck_id):
        self.truck_id = truck_id
        self.packages = []
        self.mileage = 0
        self.delivery_route = []


    def add_package(self, package):
        if len(self.packages) < 16:
            self.packages.append(package)

