parent = ''
$ ->
    $('.digest__show-more').click (ev) ->
        console.log('clicked')
        ev.preventDefault()
        parent = $(this).parent().parent()

        events = parent.find('.digest__repository-name_hidden, .digest__repository-events_hidden')
        next_events = events[0..9]
        even_more_events = events[10..]

        next_events.removeClass('digest__repository-name_hidden digest__repository-events_hidden')

        if even_more_events.length == 0
            $(this).parent().hide()


