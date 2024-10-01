import React from 'react';

const StageTimePrediction = ({
  species,
  setSpecies,
  availableSpecies,
  stages,
  setStages,
  stageInput,
  setStageInput,
  handleAddStages,
  handleRemoveStage,
  temperatures,
  setTemperatures,
  temperatureInput,
  setTemperatureInput,
  handleAddTemperatures,
  handleRemoveTemperature,
}) => {
  return (
    <div className="form-section">
      <h3>Stage Time Prediction</h3>
      
      {/* Species Input */}
      <div className="form-group">
        <label>*Enter species:</label>
        <input
          list="species-list"
          value={species}
          onChange={(e) => setSpecies(e.target.value)}
          placeholder="(e.g. Oryzias latipes)"
          className="input-field round-input"
        />
        <datalist id="species-list">
          {availableSpecies.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </datalist>
      </div>

      {/* Required Stages Input */}
      <div className="form-group">
        <label>*Enter Required Stages: </label>
        <input
          type="text"
          value={stageInput}
          onChange={(e) => setStageInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleAddStages();
            }
          }}
          placeholder="(e.g., 10, 20, 30)"
          className="input-field round-input"
        />
        <button onClick={handleAddStages} className="plus-btn">+</button>
        
        {/* Display entered stages */}
        <div className="added-values">
          {stages.map((stage) => (
            <span key={stage}>
              {stage} <span onClick={() => handleRemoveStage(stage)}>X</span>
            </span>
          ))}
        </div>
      </div>

      {/* Available Temperatures Input */}
      <div className="form-group">
        <label>*Enter Available Temperatures: </label>
        <input
          type="text"
          value={temperatureInput}
          onChange={(e) => setTemperatureInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleAddTemperatures();
            }
          }}
          placeholder="(e.g., 26, 28)"
          className="input-field round-input"
        />
        <button onClick={handleAddTemperatures} className="plus-btn">+</button>
        
        {/* Display entered temperatures */}
        <div className="added-values">
          {temperatures.map((temp) => (
            <span key={temp}>
              {temp}°C <span onClick={() => handleRemoveTemperature(temp)}>X</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StageTimePrediction;
