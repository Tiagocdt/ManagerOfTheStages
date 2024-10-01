import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Scatter } from 'react-chartjs-2';
import './Page.css';
import LoginModal from './LoginModal';
import './LoginModal.css';
import { useNavigate } from 'react-router-dom';
import DataFilter from './DataFilter'; // Import DataFilter component

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
  const [filteredGraphData, setFilteredGraphData] = useState(null); // Add this state
  const [availableSpecies, setAvailableSpecies] = useState([]);

  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
    }
  }, []);

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
    // Replace commas with periods
    if (typeof value === 'string') {
      value = value.replace(/,/g, '.');
    }

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

  const removeRow = (index) => {
    if (rows.length > 1) {
      const updatedRows = rows.filter((_, i) => i !== index);
      setRows(updatedRows);
    }
  };

  const handleEnterButtonClick = () => {
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

    // Check if the user is already authenticated
    const token = localStorage.getItem('token');
    if (token) {
      // Set the token as a default header in axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Proceed to submit the data
      submitData();
    } else {
      // Open the login modal
      setIsLoginOpen(true);
    }
  };

  const handleLogin = async (username, password) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/login', {
        username,
        password,
      });
      const token = response.data.access_token;
      // Store the token
      localStorage.setItem('token', token);
      // Set the token as a default header in axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      setIsLoginOpen(false);

      // After successful login, proceed to submit the data
      await submitData();
    } catch (error) {
      alert('Invalid credentials. Please try again.');
    }
  };

  const submitData = async () => {
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

  const handleModalClose = () => {
    setIsLoginOpen(false);
  };

  const fetchGraphData = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/get-graph-data');
      setGraphData(response.data);
      setFilteredGraphData(response.data); // Initialize filtered data
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  };

  useEffect(() => {
    // Fetch graph data on component mount
    fetchGraphData();
  }, []);

  const navigate = useNavigate();

  // Prepare data for the scatter plot
  const chartData = filteredGraphData
    ? {
        datasets: filteredGraphData.map((dataset, index) => ({
          label: `Temp ${dataset.temperature}°C`,
          data: dataset.data.map((point) => ({
            x: parseFloat(point.development_time_hpf),
            y: parseFloat(point.stage),
          })),
          backgroundColor: dataset.color,
        })),
      }
    : null;

  const handleApplyFilter = (filters) => {
    const { speciesValues, temperatureValues, stageValues, developmentTimeValues } = filters;

    // Apply filters to graphData and set filteredGraphData
    const filteredData = graphData
      .filter((dataset) => {
        // Filter datasets based on species and temperature
        let pass = true;
        if (speciesValues.length > 0) {
          pass = pass && speciesValues.includes(dataset.species);
        }
        if (temperatureValues.length > 0) {
          pass = pass && temperatureValues.includes(dataset.temperature);
        }
        return pass;
      })
      .map((dataset) => {
        // Filter data points within each dataset
        const filteredPoints = dataset.data.filter((point) => {
          let pass = true;
          if (stageValues.length > 0) {
            pass = pass && stageValues.includes(parseFloat(point.stage));
          }
          if (developmentTimeValues.length > 0) {
            pass = pass && developmentTimeValues.includes(parseFloat(point.development_time_hpf));
          }
          return pass;
        });

        if (filteredPoints.length > 0) {
          return {
            ...dataset,
            data: filteredPoints,
          };
        } else {
          return null;
        }
      })
      .filter((dataset) => dataset !== null);

    setFilteredGraphData(filteredData);
  };

  return (
    <>
      <div className={`enter-data-container ${isLoginOpen ? 'blur-background' : ''}`}>
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
                        list="species-list"
                        value={row.species}
                        onChange={(e) =>
                          handleInputChange(index, 'species', e.target.value)
                        }
                        placeholder="Species"
                        className="input-field round-input"
                      />
                      <datalist id="species-list">
                        {availableSpecies.map((s) => (
                          <option key={s} value={s} />
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
                          handleInputChange(index, 'developmentTime', e.target.value)
                        }
                        placeholder="Development Time"
                        className="input-field round-input"
                      />
                    </td>
                    {/* Remove Button */}
                    <td>
                      {rows.length > 1 && (
                        <button onClick={() => removeRow(index)} className="remove-btn">
                          -
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Add row button */}
            <div className="table-footer">
              <button onClick={addNewRow} className="add-row-btn">
                +
              </button>
            </div>

            {/* Submit button */}
            <div className="submit-btn-container">
              <button onClick={handleEnterButtonClick} className="submit-btn-predict">
                Submit
              </button>
              <button onClick={() => navigate('/edit-data')} className="edit-btn">
                Edit Data
              </button>
            </div>
          </div>

          <div className="output-container">
            <h2>Data Visualization</h2>
            {chartData ? (
              <>
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
                {/* Include DataFilter component */}
                <DataFilter data={graphData} onApplyFilter={handleApplyFilter} />
              </>
            ) : (
              <p>Loading graph...</p>
            )}
          </div>
        </div>
      </div>

      {/* Include the LoginModal component */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={handleModalClose}
        onLogin={handleLogin}
      />
    </>
  );
};

export default EnterData;