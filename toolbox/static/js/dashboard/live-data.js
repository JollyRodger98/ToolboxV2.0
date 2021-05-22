if(sessionStorage.getItem("interval_seconds") == null) {sessionStorage.setItem("interval_seconds", "10")}
$(function () {
    let interval_id = {"cpu-percent": "", "memory-percent": "", "cpu-by-core-percent": ""}
    let toggle_states = {"cpu-percent": false, "memory-percent": false, "cpu-by-core-percent": false}
    let interval_seconds = sessionStorage.getItem("interval_seconds")
    let interval_functions = {"cpu-percent": RefreshCPUTotal, "memory-percent": RefreshMemoryTotal, "cpu-by-core-percent": RefreshCPUByCore}
    let interval_id_list = []// List to save all Interval IDs in case of double/overlapping intervals

    //Select form handling and event trigger
    $("select.live-data-time-select").on("change", function () {
        interval_seconds = $(this).prop("value")
        sessionStorage.setItem("interval_seconds", $(this).prop("value"))
    }).prop("value", interval_seconds)

    // Toggle button events
    $("button.live-data-toggle").on("click", function () {
        let button_id =  $(this).attr("id")
        let button = $(this)
        if (toggle_states[button_id]){
            toggle_states[button_id] = false
            clearInterval(interval_id[button_id])
        }else if (!toggle_states[button_id]){
            interval_id[button_id] = setInterval(function (){
                interval_functions[button_id](Number(interval_seconds))
            }, Number(interval_seconds)*1000)

            interval_id_list.push(interval_id[button_id])
            toggle_states[button_id] = true
        }
        ToggleButtonStyle(button, toggle_states[button_id])
    })

    //Event handler for toggling all buttons
    $("#toggle-all").on("click", function () {
        //$("button.live-data-toggle").trigger("click")
        let icon = $(this).children("i")
        if ((icon.attr("class")).indexOf("bi-toggle-off") >= 0){
            icon.removeClass("bi-toggle-off").addClass("bi-toggle-on")
            for (const toggleStatesKey in toggle_states) {
                toggle_states[toggleStatesKey] = false
            }
        }else {
            icon.addClass("bi-toggle-off").removeClass("bi-toggle-on")
            for (const toggleStatesKey in toggle_states) {
                toggle_states[toggleStatesKey] = true
            }
            //Clears all remaining Intervals and clear list
            for (const intervalIdListKey in interval_id_list) {
                clearInterval(interval_id_list[intervalIdListKey])
            }
            interval_id_list = []
        }
        $("button.live-data-toggle").trigger("click")
    })


})

function BarClass(percentage){
    let low_threshold = 50
    let high_threshold = 75
    if (percentage < low_threshold && percentage > 0){
        //console.log("Green:" + percentage + "%")
        return "bg-success"
    }else if (percentage < high_threshold && percentage > low_threshold){
        //console.log("Yellow:" + percentage + "%")
        return "bg-warning"
    }else if (percentage < 100 && percentage > high_threshold){
        //console.log("Red:" + percentage + "%")
        return "bg-danger"
    }
}

/**Set new value for targeted percentage bar.
 * @param {number} percent_value CPU percentage value as integer.
 * @param {string} field_name Content of &lt;th> field belonging to percentage bar.
 * @return {undefined}
 */
function SetPercentageBar(percent_value, field_name){
    if (typeof(percent_value) !== "number" || typeof(percent_value) === "undefined" || isNaN(percent_value))return
    if (typeof(field_name) !== "string" || typeof(field_name) === "undefined")return
    let $elem = $(`th:contains("${field_name}")`).next().children().children()
    let [percent, percent_str] = [percent_value, `${percent_value}%`]
    $elem.attr("aria-valuenow", percent).attr("data-bs-original-title", percent_str)
        .css("width", percent_str).text(percent_str)
    $elem.removeClass("bg-success bg-warning bg-danger")
    $elem.addClass(BarClass(Number(percent)))
}

/**Calls API for CPU stats.
 *
 * @param {number} interval Timeframe in which CPU stats are collected.
 * @return {undefined}
 */
function RefreshCPUTotal(interval = 1) {
    let call =  $.get({url: "/api/hardware", dataType: "json", data: {"interval": interval, "prop": "cpu-percent"}})
    call.done(function (data, success) {
        let percentage = Number(data["cpu-percent"])
        SetPercentageBar(percentage, "CPU Usage Total")
    })
}

/**Calls API for Memory stats.
 *
 * @return {undefined}
 */
function RefreshMemoryTotal() {
    let call =  $.get({url: "/api/hardware", dataType: "json", data: {"prop": "memory-percent"}})
    call.done(function (data, success) {
        let percentage = Number(data["memory-percent"])
        SetPercentageBar(percentage, "Percent")
    })
}

/**Calls API for CPU stats by core.
 *
 * @param {number} interval Timeframe in which CPU stats are collected.
 * @return {undefined}
 */
function RefreshCPUByCore(interval = 1){
    let call =  $.get({url: "/api/hardware", dataType: "json", data: {"interval": interval, "prop": "cpu-by-core-percent"}})
    call.done(function (data, status) {
        $('th:contains("CPU Usage By Core")').next().html(
            data["cpu-by-core-percent"]
        )
    })
}

/**Change CSS classes for toggle buttons.
 *
 * @param button {JQuery<HTMLElement>} Button object
 * @param state {boolean} To which state the button will be toggled.
 * @return {undefined}
 */
function ToggleButtonStyle(button, state){
    if(state){
        button.children("i.bi-circle-fill").addClass("visually-hidden")
        button.children("div[role='status']").removeClass("visually-hidden")
    }else if (!state){
        button.children("i.bi-circle-fill").removeClass("visually-hidden")
        button.children("div[role='status']").addClass("visually-hidden")
    }
}