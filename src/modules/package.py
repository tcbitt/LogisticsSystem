class Package:
    def __init__(self, pkg_id: int, address: str, city: str, state: str, zip_code: str, deadline: str, weight_kg: int, notes: str, status: str):
        self.ID = pkg_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight_kg = weight_kg
        self.notes = notes
        self.status = status

    def print_info(self):
        print(f"Package ID: {self.ID}\n"
              f"Delivery Address: "f"{self.address}\n"
              f"City: {self.city}\n"
              f"Zip Code: {self.zip_code}\n"
              f"Deadline: {self.deadline}\n"
              f"Weight (KG): {self.weight_kg}\n"
              f"Notes: {self.notes}\n"
              f"Status: {self.status}")

    def __str__(self):
            return (f"\nPackage ID: {self.ID}\n"
            f"\tDelivery Address: "f"{self.address}\n"
            f"\tCity: {self.city}\n"
            f"\tZip Code: {self.zip_code}\n"
            f"\tDeadline: {self.deadline}\n"
            f"\tWeight (KG): {self.weight_kg}\n"
            f"\tNotes: {self.notes}\n"
            f"\tStatus: {self.status}")
