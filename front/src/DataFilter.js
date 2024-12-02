import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import './DataFilter.css'; // Import CSS for styling

const DataFilter = ({ data, onApplyFilter }) => {
  // State for options
  const [speciesOptions, setSpeciesOptions] = useState([]);
  const [temperatureOptions, setTemperatureOptions] = useState([]);
  const [stageOptions, setStageOptions] = useState([]);
  const [developmentTimeOptions, setDevelopmentTimeOptions] = useState([]);

  // State for selected filters
  const [selectedSpecies, setSelectedSpecies] = useState([]);
  const [selectedTemperatures, setSelectedTemperatures] = useState([]);
  const [selectedStages, setSelectedStages] = useState([]);
  const [selectedDevelopmentTimes, setSelectedDevelopmentTimes] = useState([]);

  useEffect(() => {
    if (!data || data.length === 0) {
      // No data available
      return;
    }

    // Prepare options from data
    const speciesSet = new Set();
    const temperatureSet = new Set();
    const stageSet = new Set();
    const developmentTimeSet = new Set();

    data.forEach(dataset => {
      if (dataset) {
        speciesSet.add(dataset.species);
        temperatureSet.add(dataset.temperature);
        if (dataset.data && dataset.data.length > 0) {
          dataset.data.forEach(point => {
            if (point) {
              const stageValue = point.stage || point.y;
              const devTimeValue = point.development_time_hpf || point.x;
              if (stageValue !== undefined && stageValue !== null) {
                stageSet.add(stageValue);
              }
              if (devTimeValue !== undefined && devTimeValue !== null) {
                developmentTimeSet.add(devTimeValue);
              }
            }
          });
        }
      }
    });

    // Convert sets to options for react-select, filtering out undefined/null values
    setSpeciesOptions(
      Array.from(speciesSet)
        .filter(s => s !== undefined && s !== null)
        .map(s => ({ value: s, label: s.toString() }))
    );

    setTemperatureOptions(
      Array.from(temperatureSet)
        .filter(t => t !== undefined && t !== null)
        .map(t => ({ value: t, label: t.toString() }))
    );

    setStageOptions(
      Array.from(stageSet)
        .filter(s => s !== undefined && s !== null)
        .map(s => ({ value: s, label: s.toString() }))
    );

    setDevelopmentTimeOptions(
      Array.from(developmentTimeSet)
        .filter(dt => dt !== undefined && dt !== null)
        .map(dt => ({ value: dt, label: dt.toString() }))
    );
  }, [data]);

  const handleApplyFilter = () => {
    // Prepare filter values
    const speciesValues = selectedSpecies.map(s => s.value);
    const temperatureValues = selectedTemperatures.map(t => parseFloat(t.value));
    const stageValues = selectedStages.map(s => parseFloat(s.value));
    const developmentTimeValues = selectedDevelopmentTimes.map(dt => parseFloat(dt.value));

    // Call the function passed via props to apply the filter
    onApplyFilter({ speciesValues, temperatureValues, stageValues, developmentTimeValues });
  };

  return (
    <div className="data-filter-container">
      <h3>Filter Options</h3>
      <div className="filter-row">
        <div className="filter-column">
          <label>Species:</label>
          <Select
            isMulti
            options={speciesOptions}
            value={selectedSpecies}
            onChange={setSelectedSpecies}
            placeholder="Select Species"
          />
        </div>
        <div className="filter-column">
          <label>Temperature:</label>
          <Select
            isMulti
            options={temperatureOptions}
            value={selectedTemperatures}
            onChange={setSelectedTemperatures}
            placeholder="Select Temperatures"
          />
        </div>
      </div>
      <div className="filter-row">
        <div className="filter-column">
          <label>Stage:</label>
          <Select
            isMulti
            options={stageOptions}
            value={selectedStages}
            onChange={setSelectedStages}
            placeholder="Select Stages"
          />
        </div>
        <div className="filter-column">
          <label>Development Time:</label>
          <Select
            isMulti
            options={developmentTimeOptions}
            value={selectedDevelopmentTimes}
            onChange={setSelectedDevelopmentTimes}
            placeholder="Select Development Times"
          />
        </div>
      </div>
      <button onClick={handleApplyFilter} className="edit-btn">
        Apply Filter
      </button>
    </div>
  );
};

export default DataFilter;
