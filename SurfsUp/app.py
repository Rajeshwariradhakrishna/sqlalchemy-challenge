# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
# Create our session (link) from Python to the DB

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

def temp_calculations(start_date, end_date):
    session = Session(engine)

    return (
        session.query(
            func.min(Measurements.tobs),
            func.avg(Measurements.tobs),
            func.max(Measurements.tobs),
        )
        .filter(Measurements.date >= start_date)
        .filter(Measurements.date <= end_date)
        .all()
    )

    # Calculate the date 1 year ago from the last data point in the database
last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
last_year = last_date - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # precipitation data from last 12 months from the most recent date from Measurement table
    prcp_data = session.query(str(Measurements.date), Measurements.prcp)\
    .filter(Measurements.date > last_year)\
    .order_by(Measurements.date).all()
    
    prcp_list = []

    #Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)
    
    #Return the JSON representation of your dictionary.
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Stations.name, Stations.station).all()

    stations_dict = dict(station_data)

    #Return a JSON list of stations from the dataset.
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    tobs_data = session.query(str(Measurements.date), Measurements.tobs)\
    .filter(Measurements.date > last_year)\
    .filter(Measurements.station == "USC00519281")\
    .order_by(Measurements.date).all()

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start, end=None):
    session = Session(engine)
    
    sel=[func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]
    
    # Query the data from start date to the end date
    start_end_data = session.query(*sel).\
                        filter(Measurements.date >= start).\
                        filter(Measurements.date <= end).all()
    start_end_list = list(np.ravel(start_end_data))

    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    return jsonify(start_end_list)
    session.close()

# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)


