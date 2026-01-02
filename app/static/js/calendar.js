
(function () {
    const raw = document.getElementById('events-data').textContent;
    let events = [];
    try { events = JSON.parse(raw) || []; } catch (e) { }

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        height: 'auto',
        locale: 'pl',
        firstDay: 1,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'multiMonthYear,dayGridMonth,timeGridWeek'
        },
        events: events,
    });
    calendar.render();
})();
