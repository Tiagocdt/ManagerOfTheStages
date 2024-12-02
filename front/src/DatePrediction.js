import React from 'react';
import DatePicker from 'react-datepicker';

const DatePrediction = ({
  commonTimeType,
  setCommonTimeType,
  startDatetime,
  setStartDatetime,
  desiredTime,
  setDesiredTime,
  collectionStart,
  setCollectionStart,
  collectionEnd,
  setCollectionEnd,
  labStart,
  setLabStart,
  labEnd,
  setLabEnd,
  selectedDays,
  setSelectedDays,
  daysOfWeek,
}) => {
  // Function to handle day selection
  const handleDayClick = (day) => {
    setSelectedDays((prevDays) =>
      prevDays.includes(day)
        ? prevDays.filter((d) => d !== day)
        : [...prevDays, day]
    );
  };

  return (
    <div className="form-section">
      <h3>Date Prediction</h3>

      {/* Switch between common Start and common End */}
      <div className="form-group">
        <label>Prediction Type:</label>
        <div className="radio-buttons">
          <label>
            <input
              type="radio"
              value="start"
              checked={commonTimeType === 'start'}
              onChange={() => setCommonTimeType('start')}
            />
            Common Start
          </label>
          <label>
            <input
              type="radio"
              value="end"
              checked={commonTimeType === 'end'}
              onChange={() => setCommonTimeType('end')}
            />
            Common End
          </label>
        </div>
      </div>

      {/* DateTime Input */}
      <div className="form-group">
        {commonTimeType === 'start' ? (
          <>
            <label>Start collection time:</label>
            <DatePicker
              selected={startDatetime}
              onChange={(date) => setStartDatetime(date)}
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={15}
              dateFormat="dd/MM/yyyy HH:mm"
              placeholderText="Select start datetime"
              className="input-field round-input"
            />
          </>
        ) : (
          <>
            <label>Desired collection time:</label>
            <DatePicker
              selected={desiredTime}
              onChange={(date) => setDesiredTime(date)}
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={15}
              dateFormat="dd/MM/yyyy HH:mm"
              placeholderText="Select desired datetime"
              className="input-field round-input"
            />
          </>
        )}
      </div>

      {/* Lab start/end time and days (visible when datetime is provided) */}
      {((commonTimeType === 'start' && startDatetime) || (commonTimeType === 'end' && desiredTime)) && (
        <>
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
        </>
      )}

      {/* Collection start/end time (only if desiredTime is provided) */}
      {commonTimeType === 'end' && desiredTime && (
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
  );
};

export default DatePrediction;
