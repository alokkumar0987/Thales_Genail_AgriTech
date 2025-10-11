# test_weather.py

from weather_agent import get_weather_alerts


def test_weather_for_indore():
    print("=== Testing Weather Advisory for Indore ===")
    result = get_weather_alerts.invoke("Indore, India")  # Call the LangChain tool
    print(result)

def test_weather_for_delhi():
    print("=== Testing Weather Advisory for Delhi ===")
    result = get_weather_alerts.invoke("Delhi, India")
    print(result)

def test_invalid_location():
    print("=== Testing Weather Advisory for Invalid Location ===")
    result = get_weather_alerts.invoke("asdfghjkl")  # nonsense location
    print(result)

if __name__ == "__main__":
    test_weather_for_indore()
    test_weather_for_delhi()
    test_invalid_location()
