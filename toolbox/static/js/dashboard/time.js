$(function () {
    NavbarDateTime()
    let timeIntervalId = NavbarTimeInterval()
    let dateIntervalId = NavbarDateInterval()
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

function set_cpu_usage_bar(percent_value) {
    let $elem = $('th:contains("CPU Usage Total")').next().children().children()
    let [percent, percent_str] = [percent_value, `${percent_value}%`]
    $elem.attr("aria-valuenow", percent).attr("data-bs-original-title", percent_str)
        .css("width", percent_str).text(percent_str)
}