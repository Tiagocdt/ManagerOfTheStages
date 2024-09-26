import React from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';

const CalendarComponent = ({ scheduleData }) => {
  const events = scheduleData.flatMap((item) => {
    const events = [];
    // Start time event
    events.push({
      title: `Start incubation for Stage ${item.stage} at ${item.temperature}°C`,
      date: item.startTime,
      backgroundColor: item.color,
    });

    // Switch time event
    if (item.switchTime) {
      events.push({
        title: `Switch to ${item.temperature2}°C for Stage ${item.stage}`,
        date: item.switchTime,
        backgroundColor: item.color2,
      });
    }

    // Collection time event
    events.push({
      title: `Collect Stage ${item.stage}`,
      date: item.collectionTime,
      backgroundColor: item.temperature2 ? item.color2 : item.color,
    });

    return events;
  });

  return (
    <FullCalendar
      plugins={[dayGridPlugin]}
      initialView="dayGridMonth"
      events={events}
      eventDisplay="block"
      height="auto"
    />
  );
};

export default CalendarComponent;
