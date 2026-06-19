"""Weather data via Open-Meteo API."""

import logging

import requests

logger = logging.getLogger(__name__)

DISTRICTS = {
    "Meerut (मेरठ)": {"lat": 28.9845, "lon": 77.7064, "region": "North"},
    "Ludhiana (लुधियाना)": {"lat": 30.9010, "lon": 75.8573, "region": "North"},
    "Karnal (करनाल)": {"lat": 29.6857, "lon": 76.9905, "region": "North"},
    "Lucknow (लखनऊ)": {"lat": 26.8467, "lon": 80.9462, "region": "North"},
    "Nashik (नासिक)": {"lat": 19.9975, "lon": 73.7898, "region": "South"},
    "Coimbatore (कोयंबटूर)": {"lat": 11.0168, "lon": 76.9558, "region": "South"},
    "Bangalore (बेंगलुरु)": {"lat": 12.9716, "lon": 77.5946, "region": "South"},
    "Hyderabad (हैदराबाद)": {"lat": 17.3850, "lon": 78.4867, "region": "South"},
    "Nagpur (नागपुर)": {"lat": 21.1458, "lon": 79.0882, "region": "Central"},
    "Patna (पटना)": {"lat": 25.5941, "lon": 85.1376, "region": "East"},
    "Kolkata (कोलकाता)": {"lat": 22.5726, "lon": 88.3639, "region": "East"},
    "Guwahati (गुवाहाटी)": {"lat": 26.1445, "lon": 91.7362, "region": "East"},
    "Ranchi (रांची)": {"lat": 23.3441, "lon": 85.3096, "region": "East"},
    "Bhubaneswar (भुवनेश्वर)": {"lat": 20.2961, "lon": 85.8245, "region": "East"},
    "Ahmedabad (अहमदाबाद)": {"lat": 23.0225, "lon": 72.5714, "region": "West"},
    "Pune (पुणे)": {"lat": 18.5204, "lon": 73.8567, "region": "West"},
    "Surat (सूरत)": {"lat": 21.1702, "lon": 72.8311, "region": "West"},
    "Indore (इंदौर)": {"lat": 22.7196, "lon": 75.8577, "region": "Central"},
    "Bhopal (भोपाल)": {"lat": 23.2599, "lon": 77.4126, "region": "Central"},
    "Raipur (रायपुर)": {"lat": 21.2514, "lon": 81.6296, "region": "Central"},
}

WEATHER_CODES = {
    0: "साफ आसमान / Clear",
    1: "ज़्यादातर साफ / Mostly clear",
    2: "आंशिक बादल / Partly cloudy",
    3: "बादल / Overcast",
    45: "कोहरा / Fog",
    48: "कोहरा / Fog",
    51: "हल्की बूंदाबांदी / Light drizzle",
    53: "बूंदाबांदी / Drizzle",
    55: "भारी बूंदाबांदी / Heavy drizzle",
    61: "हल्की बारिश / Light rain",
    63: "बारिश / Rain",
    65: "भारी बारिश / Heavy rain",
    71: "हल्की बर्फबारी / Light snow",
    73: "बर्फबारी / Snow",
    75: "भारी बर्फबारी / Heavy snow",
    80: "हल्की बौछारें / Light showers",
    81: "बौछारें / Showers",
    82: "भारी बौछारें / Heavy showers",
    95: "तूफान / Thunderstorm",
    96: "ओलावृष्टि / Hailstorm",
    99: "भारी ओलावृष्टि / Heavy hailstorm",
}


def _condition_label(code: int) -> str:
    return WEATHER_CODES.get(code, "अज्ञात / Unknown")


def get_weather(district_name: str) -> dict:
    """Fetch weather for a district from Open-Meteo API."""
    district = DISTRICTS.get(district_name)
    if not district:
        return {"error": f"District '{district_name}' not found."}

    lat = district["lat"]
    lon = district["lon"]

    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
                "timezone": "Asia/Kolkata",
                "forecast_days": 3,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        current = data.get("current_weather", {})
        daily = data.get("daily", {})

        current_code = current.get("weathercode", 0)
        current_temp = current.get("temperature", 0)
        wind_speed = current.get("windspeed", 0)

        today_max = daily.get("temperature_2m_max", [None])[0]
        today_min = daily.get("temperature_2m_min", [None])[0]
        rain_today = daily.get("precipitation_sum", [0])[0] or 0

        forecast = []
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        rains = daily.get("precipitation_sum", [])
        winds = daily.get("windspeed_10m_max", [])

        for i in range(min(3, len(dates))):
            forecast.append(
                {
                    "date": dates[i],
                    "max_temp": max_temps[i] if i < len(max_temps) else None,
                    "min_temp": min_temps[i] if i < len(min_temps) else None,
                    "rain_mm": rains[i] if i < len(rains) else 0,
                    "wind_max": winds[i] if i < len(winds) else None,
                }
            )

        return {
            "district": district_name,
            "region": district["region"],
            "current_temp": current_temp,
            "current_condition": _condition_label(current_code),
            "current_wind_kmh": wind_speed,
            "today_max": today_max,
            "today_min": today_min,
            "rain_today_mm": rain_today,
            "forecast": forecast,
        }
    except Exception as exc:
        logger.error("Weather fetch failed: %s", exc)
        return {"error": "Mausam ki jaankari abhi uplabdh nahi hai. Thodi der baad koshish karein."}
