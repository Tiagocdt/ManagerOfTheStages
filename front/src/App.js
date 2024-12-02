import React from 'react';
import { BrowserRouter as Router, Route, NavLink, Routes } from 'react-router-dom';
import PredictStages from './PredictStages';
import EnterData from './EnterData';
import './App.css'; // Ensure your CSS is imported
import HomePage from './HomePage';
import Footer from './Footer';
import EditData from './EditData';

function App() {
  return (
    <Router>
      <div>
        <header className="header">
          <h1>
            <a href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
              The Manager Of The Stages
            </a>
          </h1>
        </header>

        {/* Navigation links as buttons */}
        <nav className="nav-container">
          <NavLink to="/predict" className={({ isActive }) => isActive ? 'active-link' : ''}>
            Predict Stages
          </NavLink>
          <NavLink to="/enter" className={({ isActive }) => isActive ? 'active-link' : ''}>
            Enter Data
          </NavLink>
        </nav>

        {/* Route components */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/predict" element={<PredictStages />} />
          <Route path="/enter" element={<EnterData />} />
          <Route path="/edit-data" element={<EditData />} />
        </Routes>
        {/* Footer */}
        <Footer />
      </div>
    </Router>
  );
}

export default App;
