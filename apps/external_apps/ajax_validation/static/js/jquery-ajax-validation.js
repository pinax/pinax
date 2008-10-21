(function($)    {
    function form_data(form)   {
        return form.find("input[@checked], input[@type='text'], input[@type='hidden'], input[@type='password'], input[@type='submit'], option[@selected], textarea").filter(':enabled');
    }
    function inputs(form)   {
        return form.find("input, select, textarea")
    }
    
    $.fn.validate = function(url, settings) {
        settings = $.extend({
            type: 'table',
            callback: false,
            fields: false,
            dom: this,
            event: 'submit'
        }, settings);
        
        return this.each(function() {
            var form = $(this);
            settings.dom.bind(settings.event, function()  {
                var params = {};
                form_data(form).each(function() {
                    params[ this.name || this.id || this.parentNode.name || this.parentNode.id ] = this.value; 
                });
                
                var status = false;
                if (settings.fields) {
                    params.fields = settings.fields;
                }
                $.ajax({
                    async: false,
                    data: params,
                    dataType: 'json',
                    error: function(XHR, textStatus, errorThrown)   {
                        status = true;
                    },
                    success: function(data, textStatus) {
                        status = data.valid;
                        if (!status)    {
                            if (settings.callback)  {
                                settings.callback(data, form);
                            }
                            else    {
                                if (settings.type == 'p')    {
                                    inputs(form).parent().prev('ul').remove();
                                    inputs(form).parent().prev('ul').remove();
                                    $.each(data.errors, function(key, val)  {
                                        if (key == '__all__')   {
                                            var error = inputs(form).filter(':first').parent();
                                            if (error.prev().is('ul.errorlist')) {
                                                error.prev().before('<ul class="errorlist"><li>' + val + '</li></ul>');
                                            }
                                            else    {
                                                error.before('<ul class="errorlist"><li>' + val + '</li></ul>');
                                            }
                                        }
                                        else    {
                                            $('#' + key).parent().before('<ul class="errorlist"><li>' + val + '</li></ul>');
                                        }
                                    });
                                }
                                if (settings.type == 'table')   {
                                    inputs(form).prev('ul').remove();
                                    inputs(form).filter(':first').parent().parent().prev('tr').remove();
                                    $.each(data.errors, function(key, val)  {
                                        if (key == '__all__')   {
                                            inputs(form).filter(':first').parent().parent().before('<tr><td colspan="2"><ul class="errorlist"><li>' + val + '.</li></ul></td></tr>');
                                        }
                                        else    {
                                            $('#' + key).before('<ul class="errorlist"><li>' + val + '</li></ul>');
                                        }
                                    });
                                }
                                if (settings.type == 'ul')  {
                                    inputs(form).prev().prev('ul').remove();
                                    inputs(form).filter(':first').parent().prev('li').remove();
                                    $.each(data.errors, function(key, val)  {
                                        if (key == '__all__')   {
                                            inputs(form).filter(':first').parent().before('<li><ul class="errorlist"><li>' + val + '</li></ul></li>');
                                        }
                                        else    {
                                            $('#' + key).prev().before('<ul class="errorlist"><li>' + val + '</li></ul>');
                                        }
                                    });
                                }
                            }
                        }
                    },
                    type: 'POST',
                    url: url
                });
                return status;
            });
        });
    };
})(jQuery);
