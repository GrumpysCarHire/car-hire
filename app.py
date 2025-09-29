from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'dev-secret-change-me'  # change this for production use

# Database setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# -------------------------
# Booking Model
# -------------------------
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(200))
    pobox = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    workplace = db.Column(db.String(100))
    additional_driver = db.Column(db.String(100))
    car_type = db.Column(db.String(50))
    license_plate = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    days = db.Column(db.Integer)


# ✅ Ensure the table exists
with app.app_context():
    db.create_all()


# -------------------------
# Car data
# -------------------------
CARS = {
    "S-Presso": [
        {"id": 101, "plate": "N140-374W"},
        {"id": 102, "plate": "N161-304W"},
        {"id": 103, "plate": "N150-785W"},
        {"id": 104, "plate": "N131-797W"},
        {"id": 105, "plate": "N160-343W"},
    ],
    "Volvo": [
        {"id": 201, "plate": "Ann 8"}
    ]
}


# -------------------------
# Routes
# -------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
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
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        # Calculate days
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days
        except Exception:
            flash("Invalid dates. Please try again.")
            return redirect(url_for("index"))

        # Assign a car (first available)
        assigned_car = None
        for car in CARS[car_type]:
            conflict = Booking.query.filter(
                Booking.license_plate == car["plate"],
                Booking.start_date <= end_date,
                Booking.end_date >= start_date
            ).first()
            if not conflict:
                assigned_car = car
                break

        if not assigned_car:
            flash("No available cars for the selected type and dates.")
            return redirect(url_for("index"))

        # Save booking
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

        flash(f"Booking confirmed! Car {assigned_car['plate']} assigned.")
        return redirect(url_for("index"))

    return render_template("index.html")


# -------------------------
# Dashboard (Admin only)
# -------------------------

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "grumpy123")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    password = request.args.get("password", None)

    if password != ADMIN_PASSWORD:
        return "Access denied. Add ?password=grumpy123 to the URL.", 401

    bookings = Booking.query.order_by(Booking.start_date).all()
    return render_template("dashboard.html", bookings=bookings)


# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
