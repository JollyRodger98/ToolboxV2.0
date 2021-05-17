sessionStorage.setItem("CPUInterval", "1")
sessionStorage.setItem("CPUByCoreInterval", "1")
sessionStorage.setItem("MemoryInterval", "1")
$(function () {
    /**@type {boolean}*/
    let CPULiveToggle, MemoryLiveToggle, CPUByCoreLiveToggle
    /**@type {number}*/
    let CPUIntervalID, MemoryIntervalID, CPUByCoreIntervalID
    CPULiveToggle = MemoryLiveToggle = CPUByCoreLiveToggle = false
    /**@type {number}*/
    let CPUInterval, MemoryInterval, CPUByCoreInterval
    CPUInterval = Number(sessionStorage.getItem("CPUInterval"))
    MemoryInterval = Number(sessionStorage.getItem("MemoryInterval"))
    CPUByCoreInterval = Number(sessionStorage.getItem("CPUByCoreInterval"))


    $("#cpu-percent").on("mouseup", function () {
        if (CPULiveToggle) {
            clearInterval(CPUIntervalID)
            CPULiveToggle = false
            $(this).children().addClass("text-danger").removeClass("text-success")
        }else if (!CPULiveToggle){
            CPUIntervalID = setInterval(function (){RefreshCPUTotal()}, 1000)
            CPULiveToggle = true
            $(this).children().removeClass("text-danger").addClass("text-success")
        }
    })
    $("#memory-percent").on("mouseup", function () {
        if (MemoryLiveToggle) {
            clearInterval(MemoryIntervalID)
            MemoryLiveToggle = false
            $(this).children().addClass("text-danger").removeClass("text-success")
        }else if (!MemoryLiveToggle){
            MemoryIntervalID = setInterval(function (){RefreshMemoryTotal()}, 1000)
            MemoryLiveToggle = true
            $(this).children().removeClass("text-danger").addClass("text-success")
        }
    })
    $("#cpu-by-core-percent").on("mouseup", function () {
        if (CPUByCoreLiveToggle) {
            clearInterval(CPUByCoreIntervalID)
            CPUByCoreLiveToggle = false
            $(this).children().addClass("text-danger").removeClass("text-success")
        }else if (!CPUByCoreLiveToggle){
            CPUByCoreIntervalID = setInterval(function (){RefreshCPUByCore()}, 1000)
            CPUByCoreLiveToggle = true
            $(this).children().removeClass("text-danger").addClass("text-success")
        }
    })
})

/**Set new value for targeted percentage bar.
 * @param {number} percent_value - CPU percentage value as integer.
 * @param {string} field_name - Content of &lt;th> field belonging to percentage bar.
 * @return {undefined}
 */
function SetPercentageBar(percent_value, field_name){
    if (typeof(percent_value) !== "number" || typeof(percent_value) === "undefined" || isNaN(percent_value))return
    if (typeof(field_name) !== "string" || typeof(field_name) === "undefined")return
    let $elem = $(`th:contains("${field_name}")`).next().children().children()
    let [percent, percent_str] = [percent_value, `${percent_value}%`]
    $elem.attr("aria-valuenow", percent).attr("data-bs-original-title", percent_str)
        .css("width", percent_str).text(percent_str)
}
function RefreshCPUTotal() {
    let call =  $.get({url: "/tb-api?prop=cpu-percent", dataType: "json"})
    call.done(function (data, success) {
        let percentage = Number(data["cpu-percent"])
        SetPercentageBar(percentage, "CPU Usage Total")
    })
}
function RefreshMemoryTotal() {
    let call =  $.get({url: "/tb-api?prop=memory-percent", dataType: "json"})
    call.done(function (data, success) {
        let percentage = Number(data["memory-percent"])
        SetPercentageBar(percentage, "Percent")
    })
}
function RefreshCPUByCore(){
    let call =  $.get({url: "/tb-api?prop=cpu-by-core-percent", dataType: "json"})
    call.done(function (data, status) {
        $('th:contains("CPU Usage By Core")').next().html(
            data["cpu-by-core-percent"]
        )
    })
}