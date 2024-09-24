import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Scatter } from 'react-chartjs-2';
import './Page.css';
// Import Chart.js components
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';

// Register the components
ChartJS.register(LinearScale, PointElement, Tooltip, Legend, Title);

const EnterData = () => {
  const [rows, setRows] = useState([
    { species: '', temperature: '', stage: '', developmentTime: '' },
  ]);
  const [graphData, setGraphData] = useState(null);
  const [availableSpecies, setAvailableSpecies] = useState([]); // Holds species fetched from backend
  const [isNewSpecies, setIsNewSpecies] = useState(false); // Track if user is adding a new species

  // Fetch available species from the backend
  useEffect(() => {
    const fetchSpecies = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/get-species');
        setAvailableSpecies(response.data);
      } catch (error) {
        console.error('Error fetching species:', error);
      }
    };
    fetchSpecies();
  }, []);

  const handleInputChange = (index, field, value) => {
    const updatedRows = [...rows];
    updatedRows[index][field] = value;
    setRows(updatedRows);
  };

  const addNewRow = () => {
    setRows([
      ...rows,
      { species: '', temperature: '', stage: '', developmentTime: '' },
    ]);
  };

  const removeLastRow = () => {
    if (rows.length > 1) {
      setRows(rows.slice(0, -1));
    }
  };

  const handleSubmit = async () => {
    const isValid = rows.every(
      (row) =>
        row.species.trim() !== '' &&
        row.temperature.trim() !== '' &&
        row.stage.trim() !== '' &&
        row.developmentTime.trim() !== ''
    );

    if (!isValid) {
      alert('Please fill in all fields.');
      return;
    }

    try {
      // Send data to the backend
      await axios.post('http://127.0.0.1:5000/enter-data', { rows });
      alert('Data submitted successfully!');
      // Fetch updated graph data
      fetchGraphData();
    } catch (error) {
      console.error('Error submitting data:', error);
      alert('Error submitting data.');
    }
  };

  const fetchGraphData = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/get-graph-data');
      setGraphData(response.data);
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  };

  useEffect(() => {
    // Fetch graph data on component mount
    fetchGraphData();
  }, []);

  // Prepare data for the scatter plot
  const chartData = graphData
    ? {
        datasets: graphData.map((dataset, index) => ({
          label: `Temp ${dataset.temperature}°C`,
          data: dataset.data.map((point) => ({
            x: parseFloat(point.development_time_hpf),
            y: parseFloat(point.stage),
          })),
          backgroundColor: dataset.color,
        })),
      }
    : null;

  return (
    <div className="page-container">
      <div className="form-section">
        <h2>Enter Data</h2>
        {/* Table for data entry */}
        <table>
          <thead>
            <tr>
              <th>Species</th>
              <th>Temperature</th>
              <th>Stage</th>
              <th>Development Time (hpf)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index}>
                {/* Species dropdown and input */}
                <td>
                  <input
                    list={`species-list-${index}`}
                    value={row.species}
                    onChange={(e) => handleInputChange(index, 'species', e.target.value)}
                    placeholder="Species"
                    className="input-field round-input"
                  />
                  <datalist id={`species-list-${index}`}>
                    {availableSpecies.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </datalist>
                </td>
                {/* Temperature, Stage, and Development Time input */}
                <td>
                  <input
                    type="text"
                    value={row.temperature}
                    onChange={(e) =>
                      handleInputChange(index, 'temperature', e.target.value)
                    }
                    placeholder="Temperature"
                    className="input-field round-input"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={row.stage}
                    onChange={(e) =>
                      handleInputChange(index, 'stage', e.target.value)
                    }
                    placeholder="Stage"
                    className="input-field round-input"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={row.developmentTime}
                    onChange={(e) =>
                      handleInputChange(
                        index,
                        'developmentTime',
                        e.target.value
                      )
                    }
                    placeholder="Development Time"
                    className="input-field round-input"
                  />
                </td>
                {/* Add Remove Button here */}
                <td>
                  {rows.length > 1 && (
                    <button onClick={() => removeLastRow(index)} className="remove-btn">-</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Add row button */}
        <div className="table-footer">
          <button onClick={addNewRow} className="add-row-btn">+</button>
        </div>

        {/* Submit button */}
        <div className="submit-btn-container">
          <button onClick={handleSubmit} className="submit-btn">
            Submit
          </button>
        </div>
      </div>

      <div className="output-container">
        <h2>Data Visualization</h2>
        {chartData ? (
          <Scatter
            data={chartData}
            options={{
              scales: {
                x: {
                  type: 'linear',
                  title: { display: true, text: 'Development Time (hpf)' },
                },
                y: {
                  type: 'linear',
                  title: { display: true, text: 'Stage' },
                },
              },
            }}
          />
        ) : (
          <p>Loading graph...</p>
        )}
      </div>
    </div>
  );
};

export default EnterData;
