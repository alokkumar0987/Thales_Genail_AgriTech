import React, { useState, useEffect } from "react";
import { FaSeedling, FaCloudSun, FaChartLine } from "react-icons/fa";
import FeatureCard from "../components/FeatureCard";

const taglines = [
  "Your personalized, AI-based crop advisory system for smart and sustainable farming.",
  "स्मार्ट और टिकाऊ खेती के लिए आपकी व्यक्तिगत, एआई-आधारित फसल सलाहकार प्रणाली।", // Hindi
  "ਤੁਹਾਡੀ ਵਿਅਕਤੀਗਤ, AI-ਅਧਾਰਿਤ ਫਸਲ ਸਲਾਹ ਪ੍ਰਣਾਲੀ ਸਮਾਰਟ ਅਤੇ ਟਿਕਾਊ ਖੇਤੀ ਲਈ।",              // Punjabi
  "स्मार्ट आणि शाश्वत शेतीसाठी तुमची वैयक्तिक, एआय-आधारित पीक सल्लागार प्रणाली.",      // Marathi
  "స్మార్ట్ మరియు స్థిరమైన వ్యవసాయం కోసం మీ వ్యక్తిగతీకరించిన, AI-ఆధారిత పంట సలహా వ్యవస్థ.", // Telugu
  "ஸ்மார்ட் மற்றும் நிலையான விவசாயத்திற்கான உங்கள் தனிப்பயனாக்கப்பட்ட, AI-அடிப்படையிலான பயிர் ஆலோசனை அமைப்பு.", // Tamil
  "স্মার্ট এবং টেকসই চাষের জন্য আপনার ব্যক্তিগতকৃত, এআই-ভিত্তিক ফসল উপদেষ্টা সিস্টেম।", // Bengali
];

const HomePage = () => {
  const [currentTaglineIndex, setCurrentTaglineIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTaglineIndex((prevIndex) => (prevIndex + 1) % taglines.length);
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-50 min-h-screen pt-[16rem]"> {/* Added pt-[16rem] for custom padding-top */}
      {/* Hero Section */}
      <section className="text-center py-20 px-4 bg-white">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-4">
          Welcome to AgriHelp
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto transition-opacity duration-1000 ease-in-out">
          {taglines[currentTaglineIndex]}
        </p>
      </section>

      {/* Features Section */}
      <section className="container mx-auto py-16 px-4">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-800 mb-12">
          Our Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 items-stretch">
          {/* Chatbot Card */}
          <FeatureCard
            title="AI Chatbot"
            description="Get instant soil health and fertilizer recommendations, and detect pests with our smart assistant."
            icon={<FaSeedling />}
            linkTo="/chatbot"
          />

          {/* Weather Card */}
          <FeatureCard
            title="Weather Insights"
            description="Receive real-time weather-based alerts and predictive insights to plan your farming activities."
            icon={<FaCloudSun />}
            linkTo="/weather"
          />

          {/* Market Price Card */}
          <FeatureCard
            title="Market Price Tracking"
            description="Stay updated with the latest market prices for your crops to get the best value for your produce."
            icon={<FaChartLine />}
            linkTo="/market"
          />
        </div>
      </section>
    </div>
  );
};

export default HomePage;