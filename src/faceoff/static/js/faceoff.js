/**
 * Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

jQuery(function($) {
    // trigger bootstrap opt-in apis
    $('a.tip').tooltip();

    // logout confirmation
    $('#logout').click(function() {
        return confirm($(this).attr('data-confirm'));
    });

    // report form
    $('#report').submit(function() {
        $(this).find('button[type=submit]').attr('disabled', true);
    });
    setTimeout(function() {
        $('#report button[type=submit]').attr('disabled', false);
    }, 2000);
});
