import React, { useState } from 'react';
import './Page.css'; // Assuming you already have a CSS file for styling

const EnterData = () => {
  const [rows, setRows] = useState([{ species: '', temperature: '', stage: '', developmentTime: '' }]);

  const handleInputChange = (index, field, value) => {
    const updatedRows = [...rows];
    updatedRows[index][field] = value;
    setRows(updatedRows);
  };

  const addNewRow = () => {
    setRows([...rows, { species: '', temperature: '', stage: '', developmentTime: '' }]);
  };

  const removeLastRow = () => {
    if (rows.length > 1) {
      setRows(rows.slice(0, -1));
    }
  };

  const handleSubmit = () => {
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

    console.log('Data submitted:', rows);
    alert('Data submitted successfully!');
  };

  return (
    <div className="page-container">
      {/* Left side: Form inputs */}
      <div className="left-side">
        <h2>Enter Data</h2>

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
                <td>
                  <input
                    type="text"
                    value={row.species}
                    onChange={(e) =>
                      handleInputChange(index, 'species', e.target.value)
                    }
                    placeholder="Species"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={row.temperature}
                    onChange={(e) =>
                      handleInputChange(index, 'temperature', e.target.value)
                    }
                    placeholder="Temperature (e.g., 25°C)"
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
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={row.developmentTime}
                    onChange={(e) =>
                      handleInputChange(index, 'developmentTime', e.target.value)
                    }
                    placeholder="Development Time (hpf)"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Add and Remove row buttons */}
        <div className="button-group">
          <button onClick={addNewRow} className="add-row-btn">+</button>
          <button onClick={removeLastRow} className="remove-row-btn">-</button>
        </div>

        {/* Submit button */}
        <div className="submit-btn-container">
          <button onClick={handleSubmit} className="submit-btn">
            Submit
          </button>
        </div>
      </div>

      {/* Placeholder for Output (for later integration) */}
      <div className="output-section">
        <h3>Data Visualization</h3>
        <p>Your results will be displayed here after submission.</p>
        <pre>{JSON.stringify(rows, null, 2)}</pre>
      </div>
    </div>
  );
};

export default EnterData;
