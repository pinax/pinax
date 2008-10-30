jQuery.fn.autoscroll = function() {
    $('html,body').animate({scrollTop: this.offset().top}, 500);
}
function toggle_comment_form(id){
    var cform = $('#comment_form_' + id);
    if(cform.hasClass('hidden')) {
        cform.prev().text("Stop Replying to This Post");
        cform.slideDown();
    }
    else {
        cform.prev().text("Reply to This Post");
        cform.slideUp();
    }
    cform.toggleClass('hidden');
}
$(function() {
    var profile_avatar = $('#profile_avatar');
    if(profile_avatar) {
        profile_avatar.bind('mouseenter', function() {
            $('#avatar_replace').css('display', 'block');
        }).bind('mouseleave', function() {
            $('#avatar_replace').css('display', 'none');
        });
    }
});