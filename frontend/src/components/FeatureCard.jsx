// src/components/FeatureCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const FeatureCard = ({ title, description, icon, linkTo }) => {
  return (
    <Link to={linkTo} className="block h-full"> {/* Added h-full here */}
      <div className="bg-green-50 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 transform hover:scale-105 flex flex-col h-full"> {/* Changed bg-white to bg-green-50 and added flex flex-col h-full */}
        <div className="text-4xl text-green-600 mb-4">{icon}</div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-600 flex-grow">{description}</p> {/* Added flex-grow */}
      </div>
    </Link>
  );
};

export default FeatureCard;