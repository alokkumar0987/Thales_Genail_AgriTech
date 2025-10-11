import React, { useState, useEffect } from 'react';
import { FaArrowUp, FaArrowDown, FaSearch } from 'react-icons/fa';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';

const MarketPricePage = () => {
  const [marketData, setMarketData] = useState({ local: [], global: [] });
  const [selectedScope, setSelectedScope] = useState('local');
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCrops, setFilteredCrops] = useState([]);
  const [chartType, setChartType] = useState('timeseries');
  const [loading, setLoading] = useState(true);

  // ✅ Fetch data only once on mount
  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:8000/api/market-data/comprehensive');
        const data = await response.json();
        setMarketData(data.data);
        setFilteredCrops(data.data.local);
        setSelectedCrop(data.data.local[0]);
      } catch (error) {
        console.error("Error fetching market data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
  }, []); // <--- empty dependency = only runs once

  // ✅ Search crop filter (runs when searchTerm or selectedScope changes)
  useEffect(() => {
    if (!marketData[selectedScope]) return;
    const result = marketData[selectedScope].filter(crop =>
      crop.crop.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCrops(result);
    setSelectedCrop(result[0] || null);
  }, [searchTerm, selectedScope, marketData]);

  const handleCardClick = (crop) => setSelectedCrop(crop);
  const cropsToDisplay = marketData[selectedScope] || [];
  const chartData = selectedCrop?.price_history || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <p className="text-gray-600 text-lg font-semibold animate-pulse">Loading market data...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen pt-40 px-4">
      <div className="container mx-auto p-6 bg-white shadow-lg rounded-lg">
        <h1 className="text-3xl font-bold text-gray-800 text-center mb-6">
          Market Price Analysis
        </h1>

        {/* Toggle Local / Global */}
        <div className="flex justify-center space-x-4 mb-8">
          <button
            onClick={() => setSelectedScope('local')}
            className={`px-6 py-2 rounded-full font-semibold transition ${selectedScope === 'local' ? 'bg-green-700 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Local Crops
          </button>
          <button
            onClick={() => setSelectedScope('global')}
            className={`px-6 py-2 rounded-full font-semibold transition ${selectedScope === 'global' ? 'bg-green-700 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Global Crops
          </button>
        </div>

        {/* Search Bar */}
        <div className="flex justify-center mb-8">
          <div className="relative w-full max-w-md">
            <input
              type="text"
              placeholder="Search for a crop..."
              className="w-full px-4 py-2 pl-10 border rounded-full focus:outline-none focus:ring-2 focus:ring-green-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <FaSearch className="absolute top-1/2 left-3 transform -translate-y-1/2 text-gray-400" />
          </div>
        </div>

        {/* Crop Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {filteredCrops.length > 0 ? (
            filteredCrops.map((crop, index) => (
              <div
                key={index}
                onClick={() => handleCardClick(crop)}
                className={`bg-green-50 rounded-lg p-6 shadow-md cursor-pointer hover:shadow-lg transition-shadow duration-300 ${selectedCrop === crop ? 'ring-2 ring-green-700' : ''}`}
              >
                <h2 className="text-xl font-bold text-gray-800 mb-2">{crop.crop}</h2>
                <p className="text-sm text-gray-600 mb-4">Location: {crop.location}</p>
                <div className="flex items-center space-x-2 text-3xl font-bold mb-2">
                  <span className={crop.trend === 'increasing' ? 'text-green-500' : 'text-red-500'}>
                    {crop.trend === 'increasing' ? <FaArrowUp /> : <FaArrowDown />}
                  </span>
                  <span className="text-gray-800">{crop.price}{selectedScope === 'local' ? '₹' : '$'}</span>
                </div>
                <p className="text-gray-600">Current Price</p>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center text-gray-500">No crops found.</div>
          )}
        </div>

        {/* Crop Report */}
        {selectedCrop && (
          <div className="bg-gray-100 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">{selectedCrop.crop} Report ({selectedCrop.location})</h2>

            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-700 mb-2">Trend</h3>
              <p className="text-gray-600">{selectedCrop.trend}</p>
            </div>

            <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-700">
              <h3 className="text-lg font-bold text-green-700 mb-2">Recommendations</h3>
              <p className="text-gray-800">{selectedCrop.recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketPricePage;

