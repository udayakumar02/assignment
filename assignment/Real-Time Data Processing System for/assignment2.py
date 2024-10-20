from flask import Flask, render_template
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
import requests
import time
import smtplib
import matplotlib.pyplot as plt
import os


app = Flask(__name__)


Base = declarative_base()
engine = create_engine('sqlite:///weather.db')
Session = sessionmaker(bind=engine)

class WeatherSummary(Base):
    __tablename__ = 'weather_summary'
    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    avg_temp = Column(Float)
    max_temp = Column(Float)
    min_temp = Column(Float)
    dominant_condition = Column(String)


Base.metadata.create_all(engine)


API_KEY = 'd1bdd6cd69d082af0675144e013bfa5a' 
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
THRESHOLD_TEMP = 35 


EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'udaya85619@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_password@1')



def get_weather_data(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for {city}: {e}")
        return None

def kelvin_to_celsius(kelvin):
   
    return kelvin - 273.15

def store_weather_data(city, temp, max_temp, min_temp, condition):
    
    with Session() as session:
        summary = WeatherSummary(
            city=city,
            avg_temp=temp,
            max_temp=max_temp,
            min_temp=min_temp,
            dominant_condition=condition,
        )
        session.add(summary)
        session.commit()

def main():
    try:
        while True:
            for city in CITIES:
                data = get_weather_data(city)

                if data and 'main' in data:
                    temp = kelvin_to_celsius(data['main']['temp'])
                    max_temp = kelvin_to_celsius(data['main']['temp_max'])
                    min_temp = kelvin_to_celsius(data['main']['temp_min'])
                    condition = data['weather'][0]['main']

                    print(f"{city}: {temp:.2f}°C (Feels like: {kelvin_to_celsius(data['main']['feels_like']):.2f}°C)")

                    store_weather_data(city, temp, max_temp, min_temp, condition)
                else:
                    print(f"Skipping {city} due to missing data.")

            print("Waiting for 5 minutes...")
            time.sleep(300)  
    except KeyboardInterrupt:
        print("Weather monitoring stopped.")

@app.route('/')
def index():
    """Render the weather summary page."""
    with Session() as session:
        summaries = session.query(WeatherSummary).order_by(WeatherSummary.date.desc()).all()
    return render_template('index.html', summaries=summaries)

if __name__ == "__main__":
    from threading import Thread
    weather_thread = Thread(target=main)
    weather_thread.start()
    

    app.run(debug=True)
