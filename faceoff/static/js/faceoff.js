/**
 * Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

jQuery(function($) {
    // disable certain anchors
    $('a[href=#]').click(function(e) {
        e.preventDefault();
    });

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

    // history filter
    $('#history-filter select').change(function() {
        var sel = $(this),
            url = sel.parent('form').attr('action');
        window.location = url + sel.val();
    });

    // back buttons
    $('a.go-back').click(function() {
        history && history.go(-1);
        return false;
    });
});
