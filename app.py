from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration (SQLite file called bookings.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pobox = db.Column(db.String(50), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    workplace = db.Column(db.String(100), nullable=True)
    additional_driver = db.Column(db.String(100), nullable=True)
    car_type = db.Column(db.String(50), nullable=False)
    license_plate = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Booking {self.name} {self.surname}>"

# Car availability
cars = {
    "S-Presso": [
        {"id": 101, "plate": "N140-374W"},
        {"id": 102, "plate": "N161-304W"},
        {"id": 103, "plate": "N150-785W"},
        {"id": 104, "plate": "N131-797W"},
        {"id": 105, "plate": "N160-343W"},
    ],
    "Volvo": [
        {"id": 201, "plate": "Ann 8"},
    ]
}

def assign_car(car_type, start_date, end_date):
    # Get all bookings for this car type
    booked = Booking.query.filter_by(car_type=car_type).all()

    for car in cars[car_type]:
        # Check if this car is free
        available = True
        for b in booked:
            if b.license_plate == car["plate"]:
                if not (end_date < b.start_date or start_date > b.end_date):
                    available = False
                    break
        if available:
            return car
    return None  # No cars available

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/book", methods=["POST"])
def book():
    # Collect form data
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]
    pobox = request.form["pobox"]
    occupation = request.form["occupation"]
    workplace = request.form["workplace"]
    additional_driver = request.form["additional_driver"]
    car_type = request.form["car_type"]
    start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
    days = (end_date - start_date).days + 1

    # Assign car
    assigned_car = assign_car(car_type, start_date, end_date)
    if not assigned_car:
        return "No available cars of this type for the selected dates."

    # Save booking to database
    booking = Booking(
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        address=address,
        pobox=pobox,
        occupation=occupation,
        workplace=workplace,
        additional_driver=additional_driver,
        car_type=car_type,
        license_plate=assigned_car["plate"],
        start_date=start_date,
        end_date=end_date,
        days=days
    )
    db.session.add(booking)
    db.session.commit()

    return render_template("success.html", name=name, car=assigned_car["plate"], days=days)
from flask import Response

# Simple password for admin (change this later!)
ADMIN_PASSWORD = "grumpy123"

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Ask for password
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return Response("Access denied. Add ?password=grumpy123 to the URL.", 401)

    # Get all bookings from database
    bookings = Booking.query.all()

    return render_template("dashboard.html", bookings=bookings)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if not exist
    app.run(debug=True)
