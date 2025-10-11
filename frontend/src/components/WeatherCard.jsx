// src/components/WeatherCard.jsx
import React from 'react';
import * as FaIcons from 'react-icons/fa';

const WeatherCard = ({ day, date, high, low, icon, description, precipitation }) => {
  const WeatherIcon = FaIcons[icon];
  return (
    <div className="flex-none w-40 p-4 bg-white rounded-lg shadow-md flex flex-col items-center text-center">
      <h3 className="font-bold text-gray-800">{day}</h3>
      <p className="text-sm text-gray-500 mb-2">{date}</p>
      {WeatherIcon && <WeatherIcon className="text-4xl text-green-500 mb-2" />}
      <p className="text-lg font-semibold text-gray-800">{high}°C / {low}°C</p>
      <p className="text-sm text-gray-600">{description}</p>
      {precipitation > 0 && (
        <p className="text-xs text-blue-500 mt-1">Precipitation: {precipitation}%</p>
      )}
    </div>
  );
};

export default WeatherCard;