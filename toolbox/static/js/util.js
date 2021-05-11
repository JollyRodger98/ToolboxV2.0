function get_weekday(day){
    if(!day || typeof(day) != "number") return
    let weekdays = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag']
    return weekdays[day];
}

function get_month(month){
    if(!month || typeof(month) != "number") return
    let months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    return months[month];
}

function pad(num, size) {
    num = num.toString();
    while (num.length < size) num = "0" + num;
    return num;
}
