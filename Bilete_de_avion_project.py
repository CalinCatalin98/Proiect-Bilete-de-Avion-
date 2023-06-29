import random
import string
import sqlite3

class Flight:
    def __init__(self, flight_number, destination, departure_date, departure_time, price):
        self.flight_number = flight_number
        self.destination = destination
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.price = price
        self.available_seats = 10

class FlightManager:
    def __init__(self):
        self.flights = [
            Flight("001", "New York", "2023-06-01", "10:00", 1500),
            Flight("002", "London", "2023-06-02", "12:30", 1200),
            Flight("003", "Paris", "2023-06-03", "14:45", 1100),
            Flight("004", "Tokyo", "2023-06-04", "16:20", 2000),
            Flight("005", "Sydney", "2023-06-05", "18:10", 1800),
            Flight("006", "Roma",  "2023-06-06", "19:25",900),
            Flight("007", "Barcelona", "2023-06-10"," 22:30",1300)
        ]

    def display_flights(self):
        print("Zboruri disponibile:")
        print("---------------------")
        print("Nr. Destinație     Data         Ora       Preț")
        print("---------------------------------------------")
        for i, flight in enumerate(self.flights):
            print(f"{i+1}.  {flight.destination}  {flight.departure_date}  {flight.departure_time}  {flight.price} lei")
        print()

class Passenger:
    def __init__(self, name):
        self.name = name
        self.reservations = []

    def reserve_flight(self, flight):
        if flight.available_seats == 0:
            print("Nu mai sunt locuri disponibile pentru acest zbor.")
            return

        if flight in self.reservations:
            print("Ați rezervat deja un bilet pentru acest zbor.")
            return

        reservation_code = self.generate_reservation_code()
        self.save_reservation(flight, reservation_code)
        self.reservations.append(flight)

        print("Rezervarea a fost efectuată cu succes!")
        print(f"Cod de rezervare: {reservation_code}")

    @staticmethod
    def generate_reservation_code():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    def save_reservation(self, flight, reservation_code):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS reservations (passenger_name TEXT, flight_number TEXT, reservation_code TEXT)"
        )

        cursor.execute(
            "INSERT INTO reservations VALUES (?, ?, ?)",
            (self.name, flight.flight_number, reservation_code)
        )

        connection.commit()
        connection.close()

    def cancel_reservation(self, reservation_code):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM reservations WHERE passenger_name=? AND reservation_code=?", (self.name, reservation_code))
        reservation = cursor.fetchone()

        if reservation is not None:
            flight_number = reservation[1]
            cursor.execute("DELETE FROM reservations WHERE passenger_name=? AND reservation_code=?", (self.name, reservation_code))
            connection.commit()
            connection.close()

            for flight in self.reservations:
                if flight.flight_number == flight_number:
                    self.reservations.remove(flight)
                    flight.available_seats += 1
                    break

            print("Rezervarea a fost anulată.")
        else:
            connection.close()
            print("Nu există o rezervare pentru acest cod.")


    def find_reservation(self, reservation_code):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM reservations WHERE passenger_name=? AND reservation_code=?", (self.name, reservation_code))
        reservation = cursor.fetchone()

        if reservation:
            flight_number = reservation[1]
            cursor.execute("SELECT * FROM flights WHERE flight_number=?", (flight_number,))
            flight_data = cursor.fetchone()

            flight = Flight(flight_data[0], flight_data[1], flight_data[2], flight_data[3], flight_data[4])
            connection.close()

            return flight
        else:
            connection.close()
            return flight

    def display_details(self):
        print(f"Detalii pasager:")
        print(f"Nume: {self.name}")
        print("Rezervări:")
        if self.reservations:
            for i, flight in enumerate(self.reservations):
                print(f"{i+1}. Zbor #{flight.flight_number}")
                print(f"   Destinație: {flight.destination}")
                print(f"   Data și ora plecării: {flight.departure_date} {flight.departure_time}")
                print(f"   Preț bilet: {flight.price} lei")
                print()
        else:
            print("Nu există rezervări pentru acest pasager.")


def main():
    try:
        flight_manager = FlightManager()
        passenger = None

        connection = sqlite3.connect("reservations.db")
        connection.close()

        while True:
            print("\nMeniu Principal:")
            print("1. Vizualizare zboruri disponibile")
            print("2. Rezervare bilet de avion")
            print("3. Anulare rezervare")
            print("4. Vizualizare detalii pasager")
            print("5. Ieșire")

            choice = input("Selectați o opțiune: ")

            if choice == "1":
                flight_manager.display_flights()
            elif choice == "2":
                if not flight_manager.flights:
                    print("Nu există zboruri disponibile.")
                    continue

                if not passenger:
                    name = input("Introduceți numele pasagerului: ")
                    if name.strip() == "":
                        print("Numele pasagerului nu poate fi gol.")
                        continue

                    passenger = Passenger(name)

                flight_manager.display_flights()
                flight_choice = input("Selectați un număr de zbor: ")
                try:
                    flight_choice = int(flight_choice) - 1
                    if 0 <= flight_choice < len(flight_manager.flights):
                        flight = flight_manager.flights[flight_choice]
                        passenger.reserve_flight(flight)
                    else:
                        print("Opțiune invalidă.")
                except ValueError:
                    print("Introduceți un număr valid pentru zbor.")
            elif choice == "3":
                if not passenger:
                    print("Nu a fost introdus un nume de pasager.")
                    continue

                reservation_code = input("Introduceți codul de rezervare: ")
                if reservation_code.strip() == "":
                    print("Codul de rezervare nu poate fi gol.")
                    continue

                flight = passenger.find_reservation(reservation_code)
                if flight:
                    passenger.cancel_reservation(reservation_code)
                else:
                    print("Nu există o rezervare pentru acest cod.")
            elif choice == "4":
                if not passenger:
                    print("Nu a fost introdus un nume de pasager.")
                    continue
                passenger.display_details()
            elif choice == "5":
                break
            else:
                print("Opțiune invalidă. Vă rugăm să selectați o opțiune validă.")

    except Exception as e:
        print(f"A intervenit o eroare {str(e)}")
        print("Programul a intampinat o situatie neprevazuta si va fi inchis")


if __name__ == "__main__":
    main()