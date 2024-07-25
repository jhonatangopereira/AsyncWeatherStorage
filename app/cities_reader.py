import os

def read_cities():
    path = os.path.dirname(os.path.abspath(__file__))
    with open(f"{path}/cities.txt", "r") as file:
        cities = file.readlines()
        cities = [city.strip() for city in cities]
    return cities

if __name__ == "__main__":
    cities = read_cities()
    print(cities)