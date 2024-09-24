import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import { Scatter } from 'react-chartjs-2';
import 'react-datepicker/dist/react-datepicker.css';
import './Page.css';
// Import Chart.js components
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';

// Register the components and annotation plugin
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend, annotationPlugin);


const PredictStages = () => {
  // State variables for user inputs
  const [species, setSpecies] = useState('');
  const [availableSpecies, setAvailableSpecies] = useState([]);
  const [stages, setStages] = useState([]);
  const [stageInput, setStageInput] = useState('');
  const [temperatures, setTemperatures] = useState([]);
  const [temperatureInput, setTemperatureInput] = useState('');
  const [startDatetime, setStartDatetime] = useState(null);
  const [desiredTimeEnabled, setDesiredTimeEnabled] = useState(false);
  const [desiredTime, setDesiredTime] = useState(null);
  const [collectionStart, setCollectionStart] = useState('');
  const [collectionEnd, setCollectionEnd] = useState('');
  const [labStart, setLabStart] = useState('');
  const [labEnd, setLabEnd] = useState('');
  const [selectedDays, setSelectedDays] = useState([]);
  // State variables for outputs
  const [graphData, setGraphData] = useState(null);
  const [scheduleData, setScheduleData] = useState([]);
  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  // Handle checkbox toggle
  const handleDesiredTimeToggle = () => {
    setDesiredTimeEnabled(!desiredTimeEnabled);
  };

  // Fetch species from the server when the component mounts
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
  
  // Function to add a stage
  const handleAddStages = () => {
    const stageList = stageInput.split(',').map(stage => stage.trim()); // Split by commas and trim spaces
    const validStages = stageList.filter(stage => {
      const stageValue = parseInt(stage, 10);
      // Check if the stage is within the valid range
      if (stageValue >= 1 && stageValue <= 40) {
        return true;
      } else {
        alert(`Invalid stage: ${stage}. Please enter values between 1 and 40.`);
        return false;
      }
    });
    const uniqueStages = validStages.filter(stage => !stages.includes(stage) && stage !== ''); // Ensure uniqueness
    setStages([...stages, ...uniqueStages]); // Add new stages to existing list
    setStageInput(''); // Clear input after adding
  };

  // Function to remove a stage from the list
  const handleRemoveStage = (stage) => {
    setStages(stages.filter((s) => s !== stage));
  };

  // Function to add a temperature
  const handleAddTemperatures = () => {
    const temps = temperatureInput.split(',').map(temp => temp.trim()); // Split by commas and trim spaces
    const validTemps = temps.filter(temp => {
      const tempValue = parseFloat(temp);
      // Check if the temperature is within the valid range
      if (tempValue >= 16 && tempValue <= 35) {
        return true;
      } else {
        alert(`Invalid temperature: ${temp}. Please enter values between 16 and 35.`);
        return false;
      }
    });
    const uniqueTemps = validTemps.filter(temp => !temperatures.includes(temp) && temp !== ''); // Ensure uniqueness
    setTemperatures([...temperatures, ...uniqueTemps]); // Add new temps to existing list
    setTemperatureInput(''); // Clear input after adding
  };

  // Function to remove a temperature from the list
  const handleRemoveTemperature = (temp) => {
    setTemperatures(temperatures.filter((t) => t !== temp));
  };

  // Function to handle day selection
  const handleDayClick = (day) => {
    setSelectedDays((prevDays) =>
      prevDays.includes(day)
        ? prevDays.filter((d) => d !== day)
        : [...prevDays, day]
    );
  };

  // Function to clear all input fields
  const clearAllFields = () => {
    setSpecies('');
    setStages([]);
    setStageInput('');
    setTemperatures([]);
    setTemperatureInput('');
    setStartDatetime(null);
    setDesiredTime(null);
    setCollectionStart('');
    setCollectionEnd('');
    setLabStart('');
    setLabEnd('');
    setSelectedDays([]);
    setGraphData(null);
    setScheduleData([]);
  };

  // Function to handle form submission
  const handleSubmit = async () => {
    // Validate inputs
    if (!species.trim()) {
      alert('Please enter a species.');
      return;
    }
    if (stages.length === 0) {
      alert('Please add at least one stage.');
      return;
    }
    if (temperatures.length === 0) {
      alert('Please add at least one temperature.');
      return;
    }

    // Prepare the data payload for the backend
    const payload = {
      required_species: species.trim(),
      required_stages: stages.map((s) => parseInt(s)),
      available_temperatures: temperatures.map((t) => parseFloat(t)),
      start_datetime: startDatetime
        ? startDatetime.toISOString().slice(0, 16).replace('T', ' ')
        : null,
      desired_time: desiredTime
        ? desiredTime.toISOString().slice(0, 16).replace('T', ' ')
        : null,
      collection_start: collectionStart,
      collection_end: collectionEnd,
      lab_days: selectedDays.map((day) => daysOfWeek.indexOf(day)),
      lab_start_time: labStart,
      lab_end_time: labEnd,
    };

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', payload);

      // Check if the response has an error
      if (response.status === 200) {
        setGraphData(response.data.graphData);
        setScheduleData(response.data.scheduleData);
      } else {
        // If the server returns an error
        alert(`Error: ${response.data.error}`);
      }
    } catch (error) {
      // If the request fails completely
      if (error.response && error.response.data) {
        alert(`Error: ${error.response.data.error}`);
      } else {
        alert('An unexpected error occurred.');
      }
    }
  };

  // Prepare data for the scatter chart
  const chartData = graphData
  ? {
      datasets: graphData.datasets.map((dataset) => ({
        label: `Temp ${dataset.temperature}°C`,
        data: dataset.data.map((point) => ({
          x: parseFloat(point.Development_Time), // X-axis is Development Time
          y: parseFloat(point.Stage), // Y-axis is Stage
        })),
        backgroundColor: dataset.color,
        borderColor: dataset.color, // Optionally use the same color for the line
        fill: false,
        showLine: true, // To connect the points with lines
      })),
    }
  : null;


  // Add horizontal gray lines for required stages
  const stageAnnotations = stages.map((stage) => ({
    type: 'line',
    scaleID: 'y',
    value: stage,
    borderColor: 'gray',
    borderWidth: 1,
    label: {
      display: true,
      content: `Stage ${stage}`,
      position: 'end',
    },
  }));

  return (
    <div className="page-container">
      <div className="form-section">
        <h2>Predict Stages</h2>

        {/* Species Input */}
        <div className="form-group">
          <label>*Enter species:</label>
          <td>
            <input
              list="species-list"
              value={species}
              onChange={(e) => setSpecies(e.target.value)}
              placeholder="Species"
              className="input-field round-input"
            />
            <datalist id="species-list">
              {availableSpecies.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </datalist>
          </td>
        </div>

        {/* Required Stages Input */}
        <div>
          <label>*Enter Required Stages: </label>
          <input
            type="text"
            value={stageInput}
            onChange={(e) => setStageInput(e.target.value)}
            placeholder="Stage number"
            className="input-field round-input"
          />
          <button onClick={handleAddStages} className="plus-btn">+</button>
          
          {/* Display entered stages */}
          <div className="added-values">
            {stages.map((stage, index) => (
              <span key={stage}>
                {stage} <span onClick={() => handleRemoveStage(stage)}>X</span>
              </span>
            ))}
          </div>
        </div>

        {/* Available Temperatures Input */}
        <div>
          <label>*Enter Available Temperatures: </label>
          <input
            type="text"
            value={temperatureInput}
            onChange={(e) => setTemperatureInput(e.target.value)}
            placeholder="e.g., 25°C"
            className="input-field round-input"
          />
          <button onClick={handleAddTemperatures} className="plus-btn">+</button>
          
          {/* Display entered temperatures */}
          <div className="added-values">
            {temperatures.map((temp, index) => (
              <span key={temp}>
                {temp}°C <span onClick={() => handleRemoveTemperature(temp)}>X</span>
              </span>
            ))}
          </div>
        </div>

        {/* Start Datetime Input */}
        <div className="form-group">
          <label>Start datetime:</label>
          <DatePicker
            selected={startDatetime}
            onChange={(date) => setStartDatetime(date)}
            showTimeSelect
            timeFormat="HH:mm"
            timeIntervals={15}
            dateFormat="Pp"
            placeholderText="Select start datetime"
            className="input-field round-input"
          />
        </div>

        <div>
          {/* Desired Time Checkbox and Input */}
          <div className="form-group">
            <input
              type="checkbox"
              id="desiredTimeCheckbox"
              checked={desiredTimeEnabled}
              onChange={handleDesiredTimeToggle}
            />
            <label htmlFor="desiredTimeCheckbox">Desired Time:</label>
            
            {desiredTimeEnabled && (
              <DatePicker
                selected={desiredTime}
                onChange={(date) => setDesiredTime(date)}
                showTimeSelect
                timeFormat="HH:mm"
                timeIntervals={15}
                dateFormat="Pp"
                placeholderText="Select desired datetime"
                className="input-field round-input"
              />
            )}
          </div>

          {/* Collection Start and End Time (Only visible when checkbox is checked) */}
          {desiredTimeEnabled && (
            <div className="form-group">
              <label>Collection start and end time:</label>
              <input
                type="time"
                value={collectionStart}
                onChange={(e) => setCollectionStart(e.target.value)}
                className="input-field round-input small-field"
              />
              <input
                type="time"
                value={collectionEnd}
                onChange={(e) => setCollectionEnd(e.target.value)}
                className="input-field round-input small-field"
              />
            </div>
          )}
        </div>

        <div className="form-group time-fields">
          <label>Lab start and end time:</label>
          <input
            type="time"
            value={labStart}
            onChange={(e) => setLabStart(e.target.value)}
            className="input-field round-input small-field"
          />
          <input
            type="time"
            value={labEnd}
            onChange={(e) => setLabEnd(e.target.value)}
            className="input-field round-input small-field"
          />
        </div>

        {/* Lab Days Selection */}
        <div className="form-group">
          <label>Select lab days:</label>
          <div className="days-container">
            {daysOfWeek.map((day) => (
              <button
                key={day}
                className={
                  selectedDays.includes(day) ? 'selected day-btn' : 'day-btn'
                }
                onClick={() => handleDayClick(day)}
              >
                {day}
              </button>
            ))}
          </div>
        </div>

        {/* Clear and Submit Buttons */}
        <div className="form-group">
          <button onClick={clearAllFields} className="clear-btn">
            Clear All
          </button>
        </div>

        <div className="form-group">
          <button onClick={handleSubmit} className="submit-btn">
            Enter
          </button>
        </div>
      </div>

      {/* Output Section */}
      <div className="output-container">
        <h2>Prediction Results</h2>
        {/* Graph Display */}
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
                  min: 1,
                  max: 40, // Limits for stages
                },
              },
              plugins: {
                annotation: {
                  annotations: stageAnnotations, // Add horizontal lines for required stages
                },
              },
            }}
          />
        ) : (
          <p>Your results will be displayed here after submission.</p>
        )}

        {/* Schedule Data Display */}
        {scheduleData.length > 0 && (
          <div>
            <h3>Scheduling Information</h3>
            {scheduleData.map((item, index) => (
              <div key={index} className="schedule-item">
                {/* Visualization of incubation periods and switches */}
                <div className="bar-container">
                  <div
                    className="bar"
                    style={{
                      width: `${item.durationPercentage}%`,
                      backgroundColor: item.color,
                    }}
                  >
                    {item.temperature}°C for {item.duration.toFixed(2)} h
                  </div>
                </div>
                <p>
                  Start: {item.startTime}, Collection: {item.collectionTime}
                </p>
                {item.switchTime && (
                  <p>
                    Switch at {item.switchTime} to {item.temperature2}°C
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictStages;
