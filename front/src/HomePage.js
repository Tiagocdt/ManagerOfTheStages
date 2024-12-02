import React from 'react';
import loadingGif from './images/MedakaDevGifSingle.gif';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-container">
      <img src={loadingGif} alt="Welcome" className="welcome-gif" />
      <h2>Welcome to the Medaka Stage Prediction Tool</h2>
    </div>
  );
};

export default HomePage;