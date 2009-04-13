jQuery.fn.autoscroll = function() {
    $('html,body').animate({scrollTop: this.offset().top}, 500);
}