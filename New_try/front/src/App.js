import React from 'react';
import { BrowserRouter as Router, Route, NavLink, Routes } from 'react-router-dom';
import PredictStages from './PredictStages';
import EnterData from './EnterData';
import './App.css'; // Ensure your CSS is imported

function App() {
  return (
    <Router>
      <div>
        <header className="header">
          <h1>The Manager Of The Stages</h1>
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
          <Route path="/predict" element={<PredictStages />} />
          <Route path="/enter" element={<EnterData />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
