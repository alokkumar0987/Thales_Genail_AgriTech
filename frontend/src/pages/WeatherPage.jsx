import React, { useState } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { FaCheckCircle, FaExclamationTriangle, FaTimesCircle, FaSun, FaCloudSun, FaCloudShowersHeavy, FaBolt } from 'react-icons/fa';
import { weatherData } from '../data/mockWeatherData';
import WeatherCard from '../components/WeatherCard';
import AdvisoryDetails from '../components/AdvisoryDetails';

// Utility function to get a detailed advisory for a specific day
const getAdvisoryDetails = (date) => {
  const forecastDay = weatherData.forecast.find(
    (day) =>
      new Date(`2025-${day.date}`).getDate() === date.getDate() &&
      new Date(`2025-${day.date}`).getMonth() === date.getMonth()
  );

  if (!forecastDay) return null;

  const rules = weatherData.advisory_rules;
  const advisory = Object.keys(rules).map((activity) => {
    const status = rules[activity].status(forecastDay);
    const message = rules[activity].message(status);
    return { activity, status, message };
  });

  return { forecast: forecastDay, advisory };
};

const WeatherPage = () => {
  const [calendarValue, onCalendarChange] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState(null);
  const [scheduledActivities, setScheduledActivities] = useState([]); // New state for booked activities
  const [selectedActivity, setSelectedActivity] = useState('');
  const [selectedDayDetails, setSelectedDayDetails] = useState(null);

  const handleDayClick = (date) => {
    setSelectedDay(date);
    setSelectedDayDetails(getAdvisoryDetails(date));
  };

  const handleBookActivity = (e) => {
    e.preventDefault();
    if (selectedActivity && selectedDay) {
      const dayAdvisory = getAdvisoryDetails(selectedDay).advisory.find(
        (item) => item.activity === selectedActivity
      );

      const newActivity = {
        activity: selectedActivity,
        day: selectedDay.toDateString(),
        advisory: dayAdvisory,
      };

      setScheduledActivities([...scheduledActivities, newActivity]);
      setSelectedActivity('');

      // Here is where you would make an API call to your backend
      // The backend would then save this data and schedule the notification
      console.log('Activity Booked:', newActivity);
    }
  };

  const weatherIcons = {
    FaSun, FaCloudSun, FaCloudShowersHeavy, FaBolt
  };
  const CurrentIcon = weatherIcons[weatherData.current.icon];

  return (
    <div className="bg-gray-50 min-h-screen pt-40 px-4">
      <div className="container mx-auto p-6 bg-white shadow-lg rounded-lg">
        <h1 className="text-3xl font-bold text-gray-800 text-center mb-6">
          Weather & Advisory
        </h1>

        {/* Today's Weather Dashboard */}
        <section className="bg-green-50 rounded-lg p-6 mb-8 shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">{weatherData.current.location}</h2>
              <p className="text-sm text-gray-600">{weatherData.current.description}</p>
            </div>
            <div className="flex items-center space-x-4">
              {CurrentIcon && <CurrentIcon className="text-5xl text-green-500" />}
              <p className="text-5xl font-bold text-gray-800">{weatherData.current.temperature}°C</p>
            </div>
          </div>
          <div className="mt-4 flex justify-around text-center text-gray-600">
            <div><p className="font-semibold">Humidity</p><p>{weatherData.current.humidity}%</p></div>
            <div><p className="font-semibold">Wind Speed</p><p>{weatherData.current.wind_speed} km/h</p></div>
            <div><p className="font-semibold">Sunrise</p><p>{weatherData.current.sunrise}</p></div>
            <div><p className="font-semibold">Sunset</p><p>{weatherData.current.sunset}</p></div>
          </div>
        </section>

        {/* Multi-Day Forecast */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">7-Day Forecast</h2>
          <div className="flex flex-nowrap overflow-x-auto space-x-4">
            {weatherData.forecast.map((day, index) => (
              <WeatherCard
                key={index}
                day={day.day}
                date={day.date}
                high={day.temp_high}
                low={day.temp_low}
                icon={day.icon}
                description={day.description}
                precipitation={day.precipitation}
              />
            ))}
          </div>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Calendar View */}
          <div className="flex flex-col items-center p-4 rounded-lg bg-gray-100">
            <h2 className="text-xl font-bold mb-4">Planning Calendar</h2>
            <Calendar
              onChange={onCalendarChange}
              value={calendarValue}
              onClickDay={handleDayClick}
              onActiveStartDateChange={({ activeStartDate }) => onCalendarChange(activeStartDate)}
            />
          </div>
          
          {/* Advisory Details & Booking Section */}
          <div className="p-4 rounded-lg bg-gray-100 flex flex-col justify-start">
            <h2 className="text-xl font-bold mb-4">Day's Advisory</h2>
            {selectedDayDetails ? (
              <>
                <AdvisoryDetails
                  forecast={selectedDayDetails.forecast}
                  advisory={selectedDayDetails.advisory}
                />
                <form onSubmit={handleBookActivity} className="mt-6 flex flex-col space-y-4">
                  <h3 className="font-bold text-gray-800">Book an Activity for this day:</h3>
                  <select
                    value={selectedActivity}
                    onChange={(e) => setSelectedActivity(e.target.value)}
                    className="p-2 border rounded-md"
                  >
                    <option value="" disabled>Select Activity</option>
                    {Object.keys(weatherData.advisory_rules).map((activity) => (
                      <option key={activity} value={activity}>{activity}</option>
                    ))}
                  </select>
                  <button type="submit" className="bg-green-700 text-white font-semibold rounded-md px-6 py-2 hover:bg-green-600 transition">
                    Book Activity
                  </button>
                </form>
              </>
            ) : (
              <p className="text-gray-600">Click a day on the calendar to see the advisory.</p>
            )}
          </div>
        </div>

        {/* Scheduled Activities Display */}
        {scheduledActivities.length > 0 && (
          <div className="p-4 bg-gray-100 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Your Scheduled Activities</h2>
            <div className="space-y-4">
              {scheduledActivities.map((plan, index) => (
                <div key={index} className="bg-green-50 p-4 rounded-lg shadow-md border-l-4 border-green-700">
                  <div className="flex items-center space-x-2 font-bold text-gray-800 mb-1">
                    {plan.advisory.status === 'Good' && <FaCheckCircle className="text-green-500" />}
                    {plan.advisory.status === 'Warning' && <FaExclamationTriangle className="text-yellow-500" />}
                    {plan.advisory.status === 'Bad' && <FaTimesCircle className="text-red-500" />}
                    <span>{plan.activity} on {plan.day}</span>
                  </div>
                  <p className="text-sm text-gray-700">{plan.advisory.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherPage;