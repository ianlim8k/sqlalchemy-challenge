import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
h_station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/2016-08-30<br/>"
        f"/api/v1.0/2016-08-30/2016-09-15<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data for last 12 months"""
    # Query precipitation data for all stations
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year = last_date[0]
    
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date <= year).\
            filter(measurement.date >= year_ago).all()

    session.close()

    prcp_results = []
    for date, precipation in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = precipation
        prcp_results.append(prcp_dict)

    return jsonify(prcp_results)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations for last 12 months"""
    # Query list of stations
    station_results = session.query(measurement.station, h_station.name).\
                      filter(measurement.station == h_station.station).\
                      group_by(measurement.station).all()

    session.close()


    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations for last 12 months"""
    # Query list of stations
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year = last_date[0]
    
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    tobs_results = session.query(measurement.date, measurement.tobs).\
                    filter(measurement.station == 'USC00519281').\
                    filter(measurement.date <= year).\
                    filter(measurement.date >= year_ago).all()

    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_results))

    return jsonify(tobs_results)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return TMIN, TAVG, TMAX greater or equal to start date """
    # Query TMIN, TAVG, TMAX
    t_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                   filter(measurement.date >= start).all()

    session.close()
   
    t_summary = []
    for min, avg, max in t_results:
        summary_dict = {}
        summary_dict["TMIN"] = min
        summary_dict["TAVG"] = avg
        summary_dict["TMAX"] = max
        t_summary.append(summary_dict)

    return jsonify(t_summary)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return TMIN, TAVG, TMAX between start date and end date """
    # Query TMIN, TAVG, TMAX
    between_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date <= end).\
                filter(measurement.date >= start).all()

    session.close()
   
    tr_summary = []
    for min, avg, max in between_results:
        s_summary_dict = {}
        s_summary_dict["TMIN"] = min
        s_summary_dict["TAVG"] = avg
        s_summary_dict["TMAX"] = max
        tr_summary.append(s_summary_dict)

    return jsonify(tr_summary)



if __name__ == '__main__':
     app.run(debug=False)
