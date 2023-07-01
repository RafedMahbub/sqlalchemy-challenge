# Import the dependencies.
import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


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
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/percipitation")
def percipitation():
    """Precipitation analysis (last 12 months of data) to a dictionary using date as the key and prcp as the value"""

    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    year_prcp = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= year_ago, Measurement.prcp != None).\
            order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list
    percipitation_last_year = []
    for date, prcp in year_prcp:
        percipitation_dict = {}
        percipitation_dict["date"] = date
        percipitation_dict["prcp"] = prcp
        percipitation_last_year.append(percipitation_dict)

    return jsonify(percipitation_last_year)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature of the most-active station for the previous year of data.
        and return JSON list of temperature"""

    session = Session(engine)
    active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    year_temp = session.query(Measurement.tobs).\
                    filter(Measurement.date >= year_ago, Measurement.station == ''.join(active_station)).\
                    order_by(Measurement.tobs).all()  
    session.close()

    # Convert list of tuples into normal list
    list_year_temp = list(np.ravel(year_temp))
    return jsonify(list_year_temp)

@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)
    temp_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    t_temp= list(np.ravel(temp_start))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}

    return jsonify(t_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):

    session = Session(engine)
    temp_end = session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start).\
                         filter(Measurement.date <= end).all()
    session.close()
    t_temp= list(np.ravel(temp_end))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}

    return jsonify(t_dict)

if __name__ == "__main__":
    app.run(debug=True)