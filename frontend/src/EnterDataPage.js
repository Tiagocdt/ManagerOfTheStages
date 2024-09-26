import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';

const EnterDataPage = () => {
  const [time, setTime] = useState('');
  const [message, setMessage] = useState('');
  const [availableTemperatures, setAvailableTemperatures] = useState([]);
  const [dataPoints, setDataPoints] = useState([]);
  const [interpolatedData, setInterpolatedData] = useState([]);

  useEffect(() => {
    // Fetch available temperatures from the backend
    const fetchAvailableTemperatures = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/available-temperatures');
        setAvailableTemperatures(response.data);
      } catch (error) {
        console.error('Error fetching available temperatures:', error);
      }
    };

    // Fetch existing data points from the backend
    const fetchDataPoints = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/data-points');
        setDataPoints(response.data);
      } catch (error) {
        console.error('Error fetching data points:', error);
      }
    };

    fetchAvailableTemperatures();
    fetchDataPoints();
  }, []);

  const handleDataSubmit = async () => {
    setMessage('');
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
          // Fetch updated data points and interpolated data from the backend
          const updatedDataPoints = await axios.get('http://127.0.0.1:5000/data-points');
          const updatedInterpolatedData = await axios.get('http://127.0.0.1:5000/interpolated-data');
          setDataPoints(updatedDataPoints.data);
          setInterpolatedData(updatedInterpolatedData.data);
        } else {
          setMessage('Error adding data');
        }
      }
    } catch (error) {
      console.error('Error sending data:', error);
      setMessage('Error adding data');
    }
  };

  const handleTemperatureChange = async (selectedTemperatures) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/interpolated-data', { temperatures: selectedTemperatures }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setInterpolatedData(response.data);
    } catch (error) {
      console.error('Error fetching interpolated data:', error);
    }
  };

  return (
    <div>
      <h2>Enter New Data Points</h2>
      <p>Enter multiple entries in the format: Temperature,Stage,DD:HH:MM; ...</p>
      <input
        type="text"
        placeholder="Enter data"
        value={time}
        onChange={e => setTime(e.target.value)}
      />
      <button onClick={handleDataSubmit}>Submit Data</button>
      {message && <div>{message}</div>}

      <h2>Available Temperatures</h2>
      <select
        multiple
        value={availableTemperatures}
        onChange={e => handleTemperatureChange(Array.from(e.target.selectedOptions, option => option.value))}
      >
        {availableTemperatures.map(temp => (
          <option key={temp} value={temp}>
            {temp}°C
          </option>
        ))}
      </select>

      <h2>Existing Data Points</h2>
      <Plot
        data={[
          {
            x: dataPoints.map(point => point.stage),
            y: dataPoints.map(point => point.duration),
            type: 'scatter',
            mode: 'markers',
            marker: {
              color: 'red'
            }
          }
        ]}
        layout={{
          width: 600,
          height: 400,
          title: 'Existing Data Points',
          xaxis: {
            title: 'Stage'
          },
          yaxis: {
            title: 'Duration (hours)'
          }
        }}
      />

      <h2>Interpolated Data</h2>
      <Plot
        data={[
          {
            x: interpolatedData.map(point => point.temperature),
            y: interpolatedData.map(point => point.stage),
            z: interpolatedData.map(point => point.duration),
            type: 'surface',
            colorscale: 'Viridis'
          }
        ]}
        layout={{
          width: 600,
          height: 400,
          title: 'Interpolated Data',
          scene: {
            xaxis: {
              title: 'Temperature (°C)'
            },
            yaxis: {
              title: 'Stage'
            },
            zaxis: {
              title: 'Duration (hours)'
            }
          }
        }}
      />
    </div>
  );
};

export default EnterDataPage;