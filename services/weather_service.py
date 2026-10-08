import requests
from datetime import datetime

class WeatherService:
    def __init__(self, api_key=''):
        self.api_key = api_key
        
    def get_weather(self, lat, lon):
        """Fetch current weather data using OpenWeather or Open-Meteo fallback"""
        if self.api_key:
            # OpenWeather integration
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={self.api_key}"
            try:
                res = requests.get(url, timeout=5)
                res.raise_for_status()
                data = res.json()
                
                weather_code = data['weather'][0]['id']
                rain_prob = 100 if (weather_code // 100 in [2, 3, 5]) else 0 # 2xx Thunderstorm, 3xx Drizzle, 5xx Rain
                
                return {
                    'success': True,
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'rain_probability': rain_prob,
                    'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p'),
                    'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p'),
                    'description': data['weather'][0]['description'].capitalize(),
                    'source': 'OpenWeather'
                }
            except Exception as e:
                print(f"OpenWeather API failed: {e}. Falling back to Open-Meteo...")
                
        # Open-Meteo fallback (Free, keyless)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&forecast_days=1&daily=precipitation_probability_max"
        try:
            res = requests.get(url, timeout=5)
            res.raise_for_status()
            data = res.json()
            
            curr = data.get('current_weather', {})
            daily = data.get('daily', {})
            rain_prob = daily.get('precipitation_probability_max', [0])[0] if daily else 0
            
            # Open-Meteo WMO weather code translation
            wmo_codes = {
                0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
                45: 'Fog', 48: 'Depositing rime fog', 51: 'Light drizzle', 53: 'Moderate drizzle',
                55: 'Dense drizzle', 61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
                71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow', 80: 'Slight rain showers',
                81: 'Moderate rain showers', 82: 'Violent rain showers', 95: 'Thunderstorm'
            }
            code = curr.get('weathercode', 0)
            desc = wmo_codes.get(code, 'Unknown weather')
            
            return {
                'success': True,
                'temperature': curr.get('temperature', 0.0),
                'humidity': 60.0,  # Open-Meteo basic current_weather endpoint does not serve humidity directly
                'wind_speed': curr.get('windspeed', 0.0),
                'rain_probability': rain_prob or (100 if code >= 51 else 0),
                'sunrise': '06:00 AM',
                'sunset': '06:30 PM',
                'description': desc,
                'source': 'Open-Meteo'
            }
        except Exception as e:
            print(f"Open-Meteo API failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_farming_recommendations(temp, humidity, rain_prob):
        """Generate specific farming advice based on weather parameters"""
        tips = []
        if rain_prob > 60:
            tips.append("High chance of rain detected. Postpone scheduled irrigation to save water.")
            tips.append("Ensure drainage channels are clear to prevent waterlogging.")
        elif temp > 35:
            tips.append("Extreme heat warning. Apply mulch around roots and increase watering frequency.")
            tips.append("Avoid applying foliar spray fertilizers during peak sunshine hours.")
        elif temp < 15:
            tips.append("Cool conditions. Cover frost-sensitive seedlings if needed.")
            tips.append("Growth rate might slow down due to lower thermal units.")
            
        if humidity > 80:
            tips.append("High humidity increases fungal spore germination. Check leaves for signs of mildew.")
        elif humidity < 35:
            tips.append("Low air humidity increases transpiration. Keep soil moist.")
            
        if not tips:
            tips.append("Optimal weather conditions. Proceed with regular cropping schedule.")
            
        return tips
