import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import './Page.css'; // Include the separate CSS file for styling

const PredictStages = () => {
  const [species, setSpecies] = useState('');
  const [stages, setStages] = useState([]);
  const [stageInput, setStageInput] = useState('');
  const [temperatures, setTemperatures] = useState([]);
  const [temperatureInput, setTemperatureInput] = useState('');
  const [startDatetime, setStartDatetime] = useState(null);
  const [desiredTime, setDesiredTime] = useState(null);
  const [collectionStart, setCollectionStart] = useState('');
  const [collectionEnd, setCollectionEnd] = useState('');
  const [labStart, setLabStart] = useState('');
  const [labEnd, setLabEnd] = useState('');
  const [selectedDays, setSelectedDays] = useState([]);

  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  // Add and remove functions for stages and temperatures
  const handleAddStage = () => {
    if (stageInput >= 1 && stageInput <= 40 && !stages.includes(stageInput)) {
      setStages([...stages, stageInput]);
      setStageInput('');
    }
  };

  const handleRemoveStage = (stage) => {
    setStages(stages.filter((s) => s !== stage));
  };

  const handleAddTemperature = () => {
    if (!temperatures.includes(temperatureInput)) {
      setTemperatures([...temperatures, temperatureInput]);
      setTemperatureInput('');
    }
  };

  const handleRemoveTemperature = (temp) => {
    setTemperatures(temperatures.filter((t) => t !== temp));
  };

  const handleDayClick = (day) => {
    setSelectedDays((prevDays) =>
      prevDays.includes(day)
        ? prevDays.filter((d) => d !== day)
        : [...prevDays, day]
    );
  };

  // Clear all fields in the form
  const clearAllFields = () => {
    setSpecies('');
    setStages([]);
    setTemperatures([]);
    setStartDatetime(null);
    setDesiredTime(null);
    setCollectionStart('');
    setCollectionEnd('');
    setLabStart('');
    setLabEnd('');
    setSelectedDays([]);
  };

  const handleSubmit = () => {
    // Here you'd handle form submission logic
    alert('Form Submitted!');
  };

  return (
    <div className="page-container">
      <div className="form-section">
        <h2>Predict Stages</h2>

        {/* Species */}
        <div className="form-group">
          <label>Enter species requested:</label>
          <input
            type="text"
            value={species}
            onChange={(e) => setSpecies(e.target.value)}
            placeholder="Species"
            className="input-field"
          />
        </div>

        {/* Required Stages */}
        <div className="form-group">
          <label>Enter required stages (1 to 40):</label>
          <input
            type="number"
            value={stageInput}
            onChange={(e) => setStageInput(e.target.value)}
            min="1"
            max="40"
            placeholder="Stage number"
            className="input-field"
          />
          <button onClick={handleAddStage} className="plus-btn">+</button>
          <div>
            <p>Added stages:</p>
            {stages.map((stage) => (
              <span key={stage} className="added-item">
                {stage}{' '}
                <button
                  className="remove-btn"
                  onClick={() => handleRemoveStage(stage)}
                >
                  x
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Available Temperatures */}
        <div className="form-group">
          <label>Enter available temperatures:</label>
          <input
            type="text"
            value={temperatureInput}
            onChange={(e) => setTemperatureInput(e.target.value)}
            placeholder="Temperature (e.g., 25°C)"
            className="input-field"
          />
          <button onClick={handleAddTemperature} className="plus-btn">+</button>
          <div>
            <p>Added temperatures:</p>
            {temperatures.map((temp) => (
              <span key={temp} className="added-item">
                {temp}{' '}
                <button
                  className="remove-btn"
                  onClick={() => handleRemoveTemperature(temp)}
                >
                  x
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Start Datetime */}
        <div className="form-group">
          <label>Start datetime (optional):</label>
          <DatePicker
            selected={startDatetime}
            onChange={(date) => setStartDatetime(date)}
            showTimeSelect
            timeFormat="HH:mm" // Use 24-hour format
            timeIntervals={15}
            dateFormat="Pp"
            placeholderText="Select start datetime"
            className="input-field"
          />
        </div>

        {/* Desired Time */}
        <div className="form-group">
          <label>Desired time (optional):</label>
          <DatePicker
            selected={desiredTime}
            onChange={(date) => setDesiredTime(date)}
            showTimeSelect
            timeFormat="HH:mm" // Use 24-hour format
            timeIntervals={15}
            dateFormat="Pp"
            placeholderText="Select desired time"
            className="input-field"
          />
        </div>

        {/* Collection Start and End Time */}
        <div className="form-group">
          <label>Collection start and end time (optional, 00:00 - 24:00):</label>
          <input
            type="time"
            value={collectionStart}
            onChange={(e) => setCollectionStart(e.target.value)}
            className="time-fields"
          />
          {' - '}
          <input
            type="time"
            value={collectionEnd}
            onChange={(e) => setCollectionEnd(e.target.value)}
            className="time-fields"
          />
        </div>

        {/* Lab Start and End Time */}
        <div className="form-group">
          <label>Lab start and end time (optional, 00:00 - 24:00):</label>
          <input
            type="time"
            value={labStart}
            onChange={(e) => setLabStart(e.target.value)}
            className="input-field small-field"
          />
          {' - '}
          <input
            type="time"
            value={labEnd}
            onChange={(e) => setLabEnd(e.target.value)}
            className="input-field small-field"
          />
        </div>

        {/* Lab Days */}
        <div className="form-group">
          <label>Select lab days:</label>
          <div className="days-container">
            {daysOfWeek.map((day) => (
              <button
                key={day}
                className={selectedDays.includes(day) ? 'selected day-btn' : 'day-btn'}
                onClick={() => handleDayClick(day)}
              >
                {day}
              </button>
            ))}
          </div>
        </div>

        {/* Clear and Submit Buttons */}
        <div className="form-group">
          <button onClick={clearAllFields} className="clear-btn">Clear All Fields</button>
        </div>

        <div className="form-group">
          <button onClick={handleSubmit} className="submit-btn">
            Enter
          </button>
        </div>
      </div>

      {/* Placeholder for Output (for later integration) */}
      <div className="output-container">
        <h3>Prediction Results</h3>
        <p>Your results will be displayed here after submission.</p>
      </div>
    </div>
  );
};

export default PredictStages;
