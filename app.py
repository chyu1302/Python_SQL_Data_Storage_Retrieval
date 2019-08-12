
#Dependencies
# Import Dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np

# Database Setup

# design a Flask api based on the queries that have just developed.
# Use FLASK to create the routes.

# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///../hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
#Base.classes.keys()

# Save references to the invoices and invoice_items tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
         f"Avalable Routes:<br/>"
         
         f"/api/v1.0/precipitation<br/>"
         f"- Dates and Temperature Observations from last year<br/>"
         
         f"/api/v1.0/stations<br/>"
         f"- List of weather stations from the dataset<br/>"

         f"/api/v1.0/tobs<br/>"
         f"- List of temperature observations (tobs) from the previous year<br/>"

         f"/api/v1.0/<start><br/>"
         f"- List of min, avg, and max temperature for a given start date<br/>"
        
         f"/api/v1.0/<start>/<end><br/>"
         f"- List of min, avg, and max temperature for a given start/end range<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of Dates and precipitation from last year"""
    # Query Invoices for Billing Country
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date <= '2017-08-18').\
        filter(Measurement.date >= '2016-08-17')

    # Convert the query results  into a dictionary using date as the key and precipitation as the value
    all_prcp = []
    for result in results:
        prcp_dict = {}
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = result[1]

        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of weather stations from the dataset """
    # Query all stations
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
    

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations from the previous year """
    # Query for all temperature observations from previous year
    results = session.query(Measurement.date, Measurement.tobs).group_by(Measurement.date).\
        filter(Measurement.date <= '2017-08-18').filter(Measurement.date >= '2016-08-17')
    # Convert the query results  into a dictionary using date as the key and temperature as the value
    all_tobs = []
    for result in results:
        tobs_list = {}
        tobs_list["date"] = result[0]
        tobs_list["tobs"] = result[1]

    all_tobs.append(tobs_list)
    return jsonify(all_tobs)

      

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a list of min, avg, max for specific dates"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results= session.query(*sel).filter(Measurement.date >= start)
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end)
    temps2 = list(np.ravel(results))
    return jsonify(temps2)

if __name__ == '__main__':
    app.run(debug= True)