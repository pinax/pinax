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