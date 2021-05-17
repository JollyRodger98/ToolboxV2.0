const toolbox = {}

$(function() {
    $('.sidebar-button').on('mouseup', function (){
        $('#sidebar').toggleClass('active')
        $('#sidebar-icon').toggleClass('invisible')
        //$('#sidebar-icon').toggleClass('bi-x bi-list')
    })

    let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});
