// src/data/mockWeatherData.js
export const weatherData = {
  // ... (current and forecast data remain the same)
  current: {
    location: "Ludhiana, Punjab",
    temperature: 32,
    description: "Clear skies",
    icon: "FaSun",
    humidity: 55,
    wind_speed: 10,
    sunrise: "05:45 AM",
    sunset: "06:30 PM",
  },
  forecast: [
    {
      day: "Fri",
      date: "Sep 12",
      temp_high: 34,
      temp_low: 25,
      description: "Clear skies",
      icon: "FaSun",
      precipitation: 0,
      wind_speed: 8,
    },
    {
      day: "Sat",
      date: "Sep 13",
      temp_high: 33,
      temp_low: 24,
      description: "Partly cloudy",
      icon: "FaCloudSun",
      precipitation: 10,
      wind_speed: 12,
    },
    {
      day: "Sun",
      date: "Sep 14",
      temp_high: 30,
      temp_low: 23,
      description: "Rain showers",
      icon: "FaCloudShowersHeavy",
      precipitation: 70,
      wind_speed: 18,
    },
    {
      day: "Mon",
      date: "Sep 15",
      temp_high: 28,
      temp_low: 22,
      description: "Thunderstorms",
      icon: "FaBolt",
      precipitation: 90,
      wind_speed: 25,
    },
    {
      day: "Tue",
      date: "Sep 16",
      temp_high: 31,
      temp_low: 23,
      description: "Mostly sunny",
      icon: "FaSun",
      precipitation: 5,
      wind_speed: 10,
    },
    {
      day: "Wed",
      date: "Sep 17",
      temp_high: 32,
      temp_low: 24,
      description: "Clear skies",
      icon: "FaSun",
      precipitation: 0,
      wind_speed: 7,
    },
    {
      day: "Thu",
      date: "Sep 18",
      temp_high: 32,
      temp_low: 24,
      description: "Clear skies",
      icon: "FaSun",
      precipitation: 0,
      wind_speed: 6,
    },
  ],
  advisory_rules: {
    'Sowing': {
      status: (forecast) => forecast.precipitation > 50 ? 'Bad' : (forecast.precipitation > 20 ? 'Warning' : 'Good'),
      message: (status) => {
        if (status === 'Bad') return 'Heavy rainfall is expected. Sowing is not recommended.';
        if (status === 'Warning') return 'Light rain is possible. Sowing is risky.';
        return 'Ideal weather for sowing.';
      }
    },
    'Harvesting': {
      status: (forecast) => forecast.precipitation > 20 ? 'Bad' : 'Good',
      message: (status) => {
        if (status === 'Bad') return 'Rain is expected. Harvesting is not recommended.';
        return 'Ideal dry weather for harvesting.';
      }
    },
    'Spraying Pesticides': {
      status: (forecast) => forecast.wind_speed > 15 ? 'Bad' : 'Good',
      message: (status) => {
        if (status === 'Bad') return 'High winds are expected. Pesticides may drift, spraying is not recommended.';
        return 'Calm weather, ideal for spraying pesticides.';
      }
    },
    'Irrigation': {
      status: (forecast) => forecast.precipitation > 50 ? 'Good' : 'Warning',
      message: (status) => {
        if (status === 'Good') return 'Heavy rain is expected, so irrigation is not needed.';
        return 'Water crops as needed.';
      }
    },
  }
};