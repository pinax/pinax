jQuery.fn.autoscroll = function() {
    $('html,body').animate({scrollTop: this.offset().top}, 500);
}

$(function() {
    $("#messages li a").click(function() {
        $(this).parent().fadeOut();
        return false;
    });
});
