import requests
from django.conf import settings

def get_weather_data(city):
    """Faz a requisição à API de clima e retorna os dados de clima e fase da lua."""
    api_key = settings.WEATHER_API_KEY
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    
    params = {
        "key": api_key,
        "q": city,
        "days": 1,
        "lang": "pt" 
    }

    try:
        response = requests.get(base_url, params=params)
        
        # Print status code and headers for debugging
        #print(f"Status Code: {response.status_code}")
        #print(f"Headers: {response.headers}")
        
        # Print the raw text response for better debugging
        #print(f"Response Text: {response.text}")

        # Verificar o código de status da resposta
        if response.status_code == 200:
            data = response.json()
            weather_info = {
                "city": data["location"]["name"],
                "temperature": data["current"]["temp_c"],
                "condition": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"],
                "moon_phase": data["forecast"]["forecastday"][0]["astro"]["moon_phase"]
            }
            return weather_info
        else:
            #print(f"Erro ao buscar dados da API. Status Code: {response.status_code}")
            #print(response.json())  # Imprimir a resposta JSON de erro da API
            return None  # Retorna None em caso de erro na requisição

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
