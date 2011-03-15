$(function() {
    $("#messages li a").click(function() {
        $(this).parent().fadeOut();
        return false;
    });
});
