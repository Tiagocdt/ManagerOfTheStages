// PredictStagesForm.js
import React, { useState } from 'react';

const PredictStagesForm = ({ onSubmit }) => {
  const [requiredStages, setRequiredStages] = useState([]);
  const [availableTemperatures, setAvailableTemperatures] = useState([]);
  const [startDateTime, setStartDateTime] = useState(null);
  const [desiredTime, setDesiredTime] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ requiredStages, availableTemperatures, startDateTime, desiredTime });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Input fields for required stages, available temperatures, start datetime, desired time */}
      <button type="submit">Predict Stages</button>
    </form>
  );
};

export default PredictStagesForm;