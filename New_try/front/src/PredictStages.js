import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Scatter } from 'react-chartjs-2';
import './Page.css';
import CalendarComponent from './CalendarComponent';
import { format, isValid } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';
import { Tooltip as ReactTooltip } from 'react-tooltip';
import loadingGif from './images/MedakaDevGifFast.gif'; 
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

import StageTimePrediction from './StageTimePrediction';
import DatePrediction from './DatePrediction';
import StageImages from './StageImages';

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
  const [commonTimeType, setCommonTimeType] = useState('start'); // 'start' or 'end'
  const [startDatetime, setStartDatetime] = useState(null);
  const [desiredTime, setDesiredTime] = useState(null);
  const [collectionStart, setCollectionStart] = useState('');
  const [collectionEnd, setCollectionEnd] = useState('');
  const [labStart, setLabStart] = useState('');
  const [labEnd, setLabEnd] = useState('');
  const [selectedDays, setSelectedDays] = useState([]);
  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  // State variables for outputs
  const [graphData, setGraphData] = useState(null);
  const [scheduleData, setScheduleData] = useState([]);

  const [viewMode, setViewMode] = useState('bar'); // 'bar' or 'calendar'

  const [isLoading, setIsLoading] = useState(false);



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

  // Add this useEffect hook
  useEffect(() => {
    if (!startDatetime) {
      // Reset lab hours and days when startDatetime is null
      setLabStart('');
      setLabEnd('');
      setSelectedDays([]);
    }
  }, [startDatetime]);

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
    setCommonTimeType('start');
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
      start_datetime:
        commonTimeType === 'start' && startDatetime
          ? `${startDatetime.getFullYear()}-${('0' + (startDatetime.getMonth() + 1)).slice(-2)}-${('0' + startDatetime.getDate()).slice(-2)} ${('0' + startDatetime.getHours()).slice(-2)}:${('0' + startDatetime.getMinutes()).slice(-2)}`
          : null,
      desired_time:
        commonTimeType === 'end' && desiredTime
          ? `${desiredTime.getFullYear()}-${('0' + (desiredTime.getMonth() + 1)).slice(-2)}-${('0' + desiredTime.getDate()).slice(-2)} ${('0' + desiredTime.getHours()).slice(-2)}:${('0' + desiredTime.getMinutes()).slice(-2)}`
          : null,
      collection_start: commonTimeType === 'end' ? collectionStart : null,
      collection_end: commonTimeType === 'end' ? collectionEnd : null,
      lab_days: selectedDays.map((day) => daysOfWeek.indexOf(day)),
      lab_start_time: labStart,
      lab_end_time: labEnd,
    };

    setIsLoading(true); // Start the loading indicator

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', payload);

      if (response.status === 200) {
        if (response.data.error) {
          alert(`Error: ${response.data.error}`);
          setGraphData(null);
          setScheduleData([]);
        } else {
          setGraphData(response.data.graphData);
          setScheduleData(response.data.scheduleData);
        }
      } else {
        alert(`Error: ${response.data.error || 'Unexpected error occurred.'}`);
      }
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        alert(`Error: ${error.response.data.error}`);
      } else {
        alert('An unexpected error occurred.');
      }
    } finally {
      setIsLoading(false); // Stop the loading indicator
    }
  };

  // Prepare data for the scatter chart
  const chartData =
    graphData && graphData.datasets && graphData.datasets.length > 0
      ? {
          datasets: graphData.datasets.map((dataset) => ({
            label: `Temp ${dataset.temperature}°C`,
            data: dataset.data.map((point) => ({
              x: parseFloat(point.Development_Time),
              y: parseFloat(point.Stage),
            })),
            backgroundColor: dataset.color,
            borderColor: dataset.color,
            fill: false,
            showLine: true,
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
      {/* Form Section */}
      <div className="form-section">
      <h2>Prediction Input</h2>
        {/* Stage Time Prediction Component */}
        <StageTimePrediction
          species={species}
          setSpecies={setSpecies}
          availableSpecies={availableSpecies}
          stages={stages}
          setStages={setStages}
          stageInput={stageInput}
          setStageInput={setStageInput}
          handleAddStages={handleAddStages}
          handleRemoveStage={handleRemoveStage}
          temperatures={temperatures}
          setTemperatures={setTemperatures}
          temperatureInput={temperatureInput}
          setTemperatureInput={setTemperatureInput}
          handleAddTemperatures={handleAddTemperatures}
          handleRemoveTemperature={handleRemoveTemperature}
        />

        {/* Date Prediction Component */}
        <DatePrediction
          commonTimeType={commonTimeType}
          setCommonTimeType={setCommonTimeType}
          startDatetime={startDatetime}
          setStartDatetime={setStartDatetime}
          desiredTime={desiredTime}
          setDesiredTime={setDesiredTime}
          collectionStart={collectionStart}
          setCollectionStart={setCollectionStart}
          collectionEnd={collectionEnd}
          setCollectionEnd={setCollectionEnd}
          labStart={labStart}
          setLabStart={setLabStart}
          labEnd={labEnd}
          setLabEnd={setLabEnd}
          selectedDays={selectedDays}
          setSelectedDays={setSelectedDays}
          daysOfWeek={daysOfWeek}
        />

        {/* Clear and Submit Buttons */}
        <div>
          <button onClick={clearAllFields} className="clear-btn">
            Clear All
          </button>
          <button onClick={handleSubmit} className="submit-btn-predict">
            Submit
          </button>
        </div>

        {/* Stage Images */}
        <StageImages stages={stages} />
      </div>

      {/* Output Section */}
      <div className="output-container">
        <h2>Prediction Results</h2>
        {/* Loading Indicator */}
        {isLoading && (
          <div className="loading-container">
            <img src={loadingGif} alt="Loading..." className="loading-gif" />
            <div className="loading-text">Loading...</div>
          </div>
        )}
        {/* Graph Display */}
        {!isLoading && (chartData ? (
          <div>
            <h3>Plotted Interpolation</h3>
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
          </div>
        ) : (
          <p>Your results will be displayed here after submission.</p>
        ))}

        {/* Schedule Data Display */}
        {!isLoading && scheduleData.length > 0 && (
          <div>
            <h3>Scheduling Information</h3>
            {/* View Mode Toggle */}
            <div className="view-toggle">
              <button
                type="button"
                onClick={() => setViewMode('bar')}
                disabled={viewMode === 'bar'}
                className={`bar-view-btn ${viewMode === 'bar' ? 'active' : ''}`}
              >
                Bar View
              </button>
              <button
                type="button"
                onClick={() => setViewMode('calendar')}
                disabled={viewMode === 'calendar'}
                className={`calendar-view-btn ${viewMode === 'calendar' ? 'active' : ''}`}
              >
                Calendar View
              </button>
            </div>
            {viewMode === 'bar' ? (
              scheduleData.map((item, index) => (
                <div key={index} className="schedule-item">
                  {/* Display the stage as title */}
                  <h4>Stage {item.stage}</h4>
                  {/* Bar container */}
                  <div className="bar-container" style={{ position: 'relative', width: '100%', height: '30px' }}>
                    {/* First incubation period */}
                    <div
                      className="bar"
                      style={{
                        width: item.temperature2 ? `${item.switchDurationPercentage}%` : '100%',
                        backgroundColor: item.color,
                        height: '100%',
                        float: 'left',
                        position: 'relative',
                      }}
                      data-tooltip-id={`bar-tooltip-${index}-1`}
                    >
                      {/* Show duration */}
                      <span style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', color: '#fff' }}>
                        {item.switchDurationPercentage ? (item.duration * item.switchDurationPercentage / 100).toFixed(2) : item.duration.toFixed(2)} h
                      </span>
                    </div>
                    {/* Tooltip for first incubation period */}
                    <ReactTooltip id={`bar-tooltip-${index}-1`} effect="solid">
                      <div>
                        <p>Temperature: {item.temperature}°C</p>
                        <p>
                          Start Time:{' '}
                          {item.startTime && isValid(new Date(item.startTime))
                            ? format(new Date(item.startTime), 'EEE dd.MM HH:mm')
                            : 'N/A'}
                        </p>
                        {item.switchTime ? (
                          <p>
                            Switch Time:{' '}
                            {item.switchTime && isValid(new Date(item.switchTime))
                              ? format(new Date(item.switchTime), 'EEE dd.MM HH:mm')
                              : 'N/A'}
                          </p>
                        ) : (
                          <p>
                            End Time:{' '}
                            {item.endTime && isValid(new Date(item.endTime))
                              ? format(new Date(item.endTime), 'EEE dd.MM HH:mm')
                              : 'N/A'}
                          </p>
                        )}
                      </div>
                    </ReactTooltip>
                    {/* Switch line */}
                    {item.switchTime && (
                      <>
                        <div
                          className="switch-line"
                          style={{
                            position: 'absolute',
                            left: `${item.switchDurationPercentage}%`,
                            top: 0,
                            bottom: 0,
                            width: '2px',
                            backgroundColor: 'black',
                          }}
                          data-tooltip-id={`switch-tooltip-${index}`}
                        ></div>
                        {/* Tooltip for switch line */}
                        <ReactTooltip id={`switch-tooltip-${index}`} effect="solid">
                          <div>
                            <p>Switch Time: {format(new Date(item.switchTime), 'EEE dd.MM HH:mm')}</p>
                          </div>
                        </ReactTooltip>
                      </>
                    )}
                    {/* Second incubation period */}
                    {item.temperature2 && (
                      <>
                        <div
                          className="bar"
                          style={{
                            width: `${item.afterSwitchDurationPercentage}%`,
                            backgroundColor: item.color2,
                            height: '100%',
                            float: 'left',
                            position: 'relative',
                          }}
                          data-tooltip-id={`bar-tooltip-${index}-2`}
                        >
                          {/* Show duration */}
                          <span style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', color: '#fff' }}>
                            {(item.duration * item.afterSwitchDurationPercentage / 100).toFixed(2)} h
                          </span>
                        </div>
                        {/* Tooltip for second incubation period */}
                        <ReactTooltip id={`bar-tooltip-${index}-2`} effect="solid">
                          <div>
                            <p>Temperature: {item.temperature2}°C</p>
                            <p>Start Time: {format(new Date(item.switchTime), 'EEE dd.MM HH:mm')}</p>
                            <p>End Time: {format(new Date(item.endTime), 'EEE dd.MM HH:mm')}</p>
                          </div>
                        </ReactTooltip>
                      </>
                    )}
                  </div>
                  {/* Start and collection times */}
                  <div className="time-labels" style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span className="start-time">
                      {item.startTime && isValid(new Date(item.startTime))
                        ? format(new Date(item.startTime), 'EEE dd.MM HH:mm')
                        : ''}
                    </span>
                    <span className="collection-time">
                      {item.endTime && isValid(new Date(item.endTime))
                        ? format(new Date(item.endTime), 'EEE dd.MM HH:mm')
                        : ''}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div>
                <CalendarComponent scheduleData={scheduleData} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictStages;
