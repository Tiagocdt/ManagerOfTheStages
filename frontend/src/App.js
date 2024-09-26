import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import PredictStagesForm from './PredictStagesForm';
import EnterDataPage from './EnterDataPage';

const App = () => {
  const [time, setTime] = useState('');
  const [message, setMessage] = useState('');
  const [view, setView] = useState('landing');

  const handleDataSubmit = async () => {
    setMessage(''); // Clear previous messages
    try {
      const dataEntries = time.split(';').map(entry => {
        const [temperature, stage, duration] = entry.split(',');
        const [days, hours, minutes] = duration.split(':').map(Number);
        const time_in_hpf = days * 24 + hours + minutes / 60;
        return { temperature: temperature.trim(), stage: stage.trim(), duration: time_in_hpf };
      });
      for (const entry of dataEntries) {
        const response = await axios.post('http://127.0.0.1:5000/enter-data', entry, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (response.status === 200) {
          setMessage('Data successfully added');
        } else {
          setMessage('Error adding data');
        }
      }
    } catch (error) {
      console.error('Error sending data:', error);
      setMessage('Error adding data');
    }
  };

  const handlePredict = async (data) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', data, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Handle the response data
      console.log(response.data);
      // Update the UI with the prediction results
    } catch (error) {
      console.error('Error predicting stages:', error);
      setMessage('Error predicting stages');
    }
  };

  const renderView = () => {
    switch (view) {
      case 'landing':
        return (
          <>
            <h1>Medaka Prediction Tool</h1>
            <button onClick={() => setView('enterData')}>Enter Data</button>
            <button onClick={() => setView('predictStages')}>Predict Stages</button>
          </>
        );
      case 'enterData':
        return <EnterDataPage />;
      case 'predictStages':
        return (
          <div>
            <h2>Predict Stages</h2>
            <PredictStagesForm onSubmit={handlePredict} />
          </div>
        );
      default:
        return null;
    }
  };

  return <div className="App">{renderView()}</div>;
};

export default App;