// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar'; // Import the new Navbar component

import HomePage from './pages/HomePage';
import ChatbotPage from './pages/ChatbotPage.jsx';
import WeatherPage from './pages/WeatherPage';
import MarketPricePage from './pages/MarketPricePage';
import LoginPage from './pages/LoginPage.jsx';
import Register from './pages/Register.jsx'
function App() {
  return (
    <Router>
      <Navbar /> {/* Place the Navbar here */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/weather" element={<WeatherPage />} />
        <Route path="/market" element={<MarketPricePage />} />
        <Route path ="/login" element={<LoginPage/>}/>
        <Route path ="/register" element={<Register/>}/>
      </Routes>
    </Router>
  );
}

export default App;