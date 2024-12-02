import React from 'react';

const StageImages = ({ stages }) => {
  return (
    <div className="stage-images-container">
      <h3>Stage Images</h3>
      <div className="stage-images">
        {stages.map((stage) => (
          <div key={stage} className="stage-image">
            <img
              src={require(`./images/stages/st${stage}.jpg`)}
              alt={`Stage ${stage}`}
            />
            <p>Stage {stage}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StageImages;