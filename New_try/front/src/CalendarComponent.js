import React from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction'; // For interactivity
import tippy from 'tippy.js';
import 'tippy.js/dist/tippy.css';
import { format } from 'date-fns';

const CalendarComponent = ({ scheduleData }) => {
  // Generate colors for each stage
  const stageColors = {};
  const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
  const uniqueStages = [...new Set(scheduleData.map(item => item.stage))];
  uniqueStages.forEach((stage, index) => {
    stageColors[stage] = colors[index % colors.length];
  });

  // Prepare events
  const events = scheduleData.flatMap((item) => {
    const events = [];
    // Start time event
    events.push({
      title: `Start Stage ${item.stage}`,
      start: item.startTime,
      backgroundColor: stageColors[item.stage],
      borderColor: stageColors[item.stage],
      extendedProps: {
        description: `Start incubation for Stage ${item.stage} at ${item.temperature}°C`,
      },
    });

    // Switch time event
    if (item.switchTime) {
      events.push({
        title: `Switch Stage ${item.stage}`,
        start: item.switchTime,
        backgroundColor: stageColors[item.stage],
        borderColor: stageColors[item.stage],
        extendedProps: {
          description: `Switch to ${item.temperature2}°C for Stage ${item.stage}`,
        },
      });
    }

    // Egg Collection time event
    events.push({
      title: `Collect Stage ${item.stage}`,
      start: item.endTime,
      backgroundColor: stageColors[item.stage],
      borderColor: stageColors[item.stage],
      extendedProps: {
        description: `Collect Stage ${item.stage}`,
      },
    });

    return events;
  });

  // Render the calendar
  return (
    <div>
      {/* Legend */}
      <div className="legend" style={{ display: 'flex', flexWrap: 'wrap' }}>
        {uniqueStages.map(stage => (
            <div key={stage} style={{ display: 'flex', alignItems: 'center', marginRight: '15px', marginBottom: '5px' }}>
                <div style={{ width: '15px', height: '15px', backgroundColor: stageColors[stage], marginRight: '5px' }}></div>
                <span>Stage {stage}</span>
            </div>
        ))}
    </div>
      <FullCalendar
        plugins={[timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'timeGridWeek,timeGridDay'
        }}
        events={events}
        eventContent={renderEventContent}
        eventDidMount={handleEventHover}
        allDaySlot={false} 
        height="400px"
      />
    </div>
  );
};

function renderEventContent(eventInfo) {
  return (
    <div>
      <span>{eventInfo.event.title}</span>
    </div>
  );
}

function handleEventHover(info) {
    const description = info.event.extendedProps.description;
    const eventStart = format(info.event.start, 'EEE dd.MM HH:mm');
    const content = `${description} at ${eventStart}`;

  tippy(info.el, {
    content: content,
    allowHTML: true,
  });
}

export default CalendarComponent;
