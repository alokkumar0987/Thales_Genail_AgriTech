import React from "react";
import { Link } from "react-router-dom";
import { FaHome, FaSeedling, FaCloudSun, FaChartLine, FaSignInAlt, FaGlobe } from "react-icons/fa";
import ashokStambh from "../assets/ashok-stambh.png";
import DynamicImageDisplay from "./DynamicImageDisplay";

const Navbar = () => {
  return (
    <div className="font-sans fixed top-0 w-full z-50 mb-10">
      {/* Top Section: Logos and Ministry Info */}
      <div className="bg-white shadow-sm py-2 px-8 flex justify-between items-center relative overflow-hidden">
        {/* Left Side: Your Project Logo/Text */}
        <div className="flex items-center space-x-4">
          <img src={ashokStambh} alt="Ashok Stambh" className="h-16" />
          <div className="flex flex-col">
            <h1 className="text-xl font-bold text-gray-800">
              स्मार्ट फसल सलाहकार प्रणाली
            </h1>
            <p className="text-gray-600 text-lg font-medium">
              SMART CROP ADVISORY SYSTEM
            </p>
            <div className="flex text-xs text-gray-700 mt-2">

              <div className="flex flex-col items-center pl-4 border-l border-gray-400">
                <span>उच्च शिक्षा विभाग</span>
                <span className="font-semibold">
                  DEPARTMENT OF HIGHER EDUCATION
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Dynamic Images */}
        <div className="absolute right-0 top-0 h-full flex items-center pr-4 md:pr-8">
          <DynamicImageDisplay images={['/image1.jpg', '/image2.jpg', '/image3.jpg', '/image4.jpg', '/image5.jpg']} />
        </div>
      </div>

      {/* Main Navigation Bar */}
      <nav className="bg-green-700 text-white shadow-lg">
        <div className="container mx-auto flex items-center justify-between px-8 py-1">
          {/* Main Links (Left-aligned) */}
          <ul className="flex items-center space-x-6 text-sm">
            <li>
              <Link
                to="/"
                className="flex items-center space-x-2 p-1 rounded hover:bg-white/10 transition"
              >
                <FaHome /><span>Home</span>
              </Link>
            </li>
            <li>
              <Link
                to="/chatbot"
                className="flex items-center space-x-2 p-1 rounded hover:bg-white/10 transition"
              >
                <FaSeedling /><span>Chatbot</span>
              </Link>
            </li>
            <li>
              <Link
                to="/weather"
                className="flex items-center space-x-2 p-1 rounded hover:bg-white/10 transition"
              >
                <FaCloudSun /><span>Weather</span>
              </Link>
            </li>
            <li>
              <Link
                to="/market"
                className="flex items-center space-x-2 p-1 rounded hover:bg-white/10 transition"
              >
                <FaChartLine /><span>Market</span>
              </Link>
            </li>
          </ul>

          {/* Right Side: Language and Login */}
          <div className="flex items-center space-x-4">
            {/* Language Dropdown */}
            <div className="flex items-center space-x-2 text-sm">
              <label htmlFor="language-select" className="text-sm font-semibold">भाषा चुनें-</label>
              <div className="relative">
                <select
                  id="language-select"
                  className="bg-green-600 text-white rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                >
                  <option value="hindi">Hindi</option>
                  <option value="english">English</option>
                </select>
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none text-white">
                  &#9662;
                </div>
              </div>
            </div>
            {/* Login Button */}
            <Link
              to="/login"
              className="flex items-center space-x-2 bg-white text-green-700 px-3 py-1 rounded-full font-bold hover:bg-gray-200 transition"
            >
              <FaSignInAlt /><span>Login</span>
            </Link>
          </div>
        </div>
      </nav>
      {/* Bottom Light Green Bar (Marquee) */}
      <div className="overflow-hidden whitespace-nowrap bg-green-100 text-green-800 py-1">
        <div className="animate-marquee inline-block px-4">
          🌾 Get real-time crop advisory | Pest detection | Soil health guidance | Market prices updated daily
        </div>
      </div>
    </div>
  );
};

export default Navbar;