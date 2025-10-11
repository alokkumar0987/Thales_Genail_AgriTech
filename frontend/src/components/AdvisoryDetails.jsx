// src/components/AdvisoryDetails.jsx
import React from 'react';
import { FaCheckCircle, FaExclamationTriangle, FaTimesCircle } from 'react-icons/fa';

const getStatusIcon = (status) => {
    if (status === 'Good') return <FaCheckCircle className="text-green-500" />;
    if (status === 'Warning') return <FaExclamationTriangle className="text-yellow-500" />;
    if (status === 'Bad') return <FaTimesCircle className="text-red-500" />;
    return null;
};

const AdvisoryDetails = ({ forecast, advisory }) => {
    return (
        <div className="p-4 bg-gray-100 rounded-lg">
            <h3 className="text-xl font-bold mb-2">Advisory for {forecast.day}, {forecast.date}</h3>
            <p className="text-sm text-gray-700 mb-4">
                Weather: {forecast.description} | High: {forecast.temp_high}°C | Low: {forecast.temp_low}°C
            </p>
            <div className="space-y-3">
                {advisory.map((item, index) => (
                    <div key={index} className="flex items-start space-x-2">
                        <div className="flex-none pt-1">{getStatusIcon(item.status)}</div>
                        <div>
                            <h4 className="font-bold text-gray-800">{item.activity}</h4>
                            <p className="text-sm text-gray-600">{item.message}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AdvisoryDetails;