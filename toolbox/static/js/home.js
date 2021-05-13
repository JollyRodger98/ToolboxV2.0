$(function () {
    NavbarDateTime()
    let timeIntervalId = NavbarTimeInterval()
    let dateIntervalId = NavbarDateInterval()

    let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});

function NavbarTimeInterval(){
    return setInterval(function () {
        $('#navbar-time').text(get_time())
    }, 1000)
}
function NavbarDateInterval(){
    return setInterval(function () {
        $('#navbar-date').text(get_date())
    }, 3600000)
}
function NavbarDateTime(){
    $('#navbar-time').text(get_time())
    $('#navbar-date').text(get_date())
}
function get_date(){
    let time = new Date()
    let weekday = get_weekday(time.getDay())
    let day = pad(time.getDate(), 2)
    let month = pad((Number(time.getMonth()) + 1), 2)
    month = get_month(time.getMonth())
    let year = time.getFullYear()
    return `${day}. ${month} ${year}`
}
function get_time(){
    let time = new Date()
    let hours = pad(time.getHours(),2)
    let minutes = pad(time.getMinutes(),2)
    let seconds = pad(time.getSeconds(), 2)
    return `${hours}:${minutes}:${seconds}`
}
