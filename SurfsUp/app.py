# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# Create an engine to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an app instance
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Route for the homepage
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

# Route to return the precipitation data for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    # Return the JSON response
    return jsonify(precipitation_data)

# Route to return a list of stations
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    stations = [station[0] for station in results]

    # Return the JSON response
    return jsonify(stations)

# Route to return temperature observations for the most active station for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Query the temperature observations for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the results to a list of temperature observations
    tobs_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    # Return the JSON response
    return jsonify(tobs_data)

# Route to return temperature statistics (TMIN, TAVG, TMAX) for a specified start date
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Query the temperature statistics from the start date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Create a dictionary to store the temperature statistics
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return the JSON response
    return jsonify(temperature_stats)

# Route to return temperature statistics for a specified start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Query the temperature statistics for the specified date range
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a dictionary to store the temperature statistics
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return the JSON response
    return jsonify(temperature_stats)

# Close the session at the end of the request
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
