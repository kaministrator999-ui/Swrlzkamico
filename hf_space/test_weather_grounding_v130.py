from model_router import _weather_grounded_text

def test_weather_grounding_uses_only_structured_widget_evidence():
    result={"kind":"weather","modelContext":{
        "location":{"label":"Leavenworth, Kansas, United States"},
        "current":{"condition":"Clear sky","temperature":66.1,"apparentTemperature":62.3,"humidity":42,"precipitation":0.0,"windSpeed":4.3},
        "units":{"temperature":"°F","precipitation":"inch","windSpeed":"mp/h"},
        "daily":[
            {"condition":"Mainly clear","high":73.7,"low":48.2},
            {"condition":"Clear sky","high":80.1,"low":51.9},
        ],
    }}
    text=_weather_grounded_text(result)
    assert "66.1°F" in text
    assert "62.3°F" in text
    assert "42%" in text
    assert "4.3mp/h" in text
    assert "73.7°F" in text and "48.2°F" in text
    assert "80.1°F" in text and "51.9°F" in text
    forbidden=["45.8443","89.6338","high elevation","Historical Data","OpenWeatherMap","weather.gov","[current timestamp]"]
    assert not any(item.lower() in text.lower() for item in forbidden)
