from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"

# SQLite database setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookings.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Car license plate pools
CAR_PLATES = {
    "S-Presso": ["N140-374W", "N161-304W", "N150-785W", "N131-797W", "N160-343W"],
    "Volvo": ["Ann 8"]
}


# Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    pobox = db.Column(db.String(50))
    occupation = db.Column(db.String(100))
    workplace = db.Column(db.String(100))
    additional_driver = db.Column(db.String(50))
    car_type = db.Column(db.String(20))
    license_plate = db.Column(db.String(20))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    days = db.Column(db.Integer)


with app.app_context():
    db.create_all()


# Home page (booking form)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Collect client details
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

        # Calculate number of days
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days
        except Exception:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for("index"))

        if days <= 0:
            flash("End date must be after start date.")
            return redirect(url_for("index"))

        # Assign a license plate (but don’t show client)
        license_plate = random.choice(CAR_PLATES.get(car_type, ["TBD"]))

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
            license_plate=license_plate,
            start_date=start_date,
            end_date=end_date,
            days=days,
        )
        db.session.add(booking)
        db.session.commit()

        # Confirmation (NO license plate shown to client)
        flash(f"Booking successful! You booked a {car_type} for {days} days.")
        return redirect(url_for("index"))

    return render_template("index.html")


# Dashboard (Admin only)
@app.route("/dashboard")
def dashboard():
    password = request.args.get("password")
    if password != "grumpy123":  # simple password check
        return "Unauthorized", 403

    bookings = Booking.query.all()
    return render_template("dashboard.html", bookings=bookings)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
