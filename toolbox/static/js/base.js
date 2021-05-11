const toolbox = {}

$(function() {
    $('.sidebar-button').on('mouseup', function (){
        $('#sidebar').toggleClass('active')
        $('#sidebar-icon').toggleClass('invisible')
        //$('#sidebar-icon').toggleClass('bi-x bi-list')
    })
});
