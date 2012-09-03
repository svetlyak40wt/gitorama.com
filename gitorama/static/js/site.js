var parent;

parent = '';

$(function() {
  return $('.digest__show-more').click(function(ev) {
    var even_more_events, events, next_events;
    console.log('clicked');
    ev.preventDefault();
    parent = $(this).parent().parent();
    events = parent.find('.digest__repository-name_hidden, .digest__repository-events_hidden');
    next_events = events.slice(0, 10);
    even_more_events = events.slice(10);
    next_events.removeClass('digest__repository-name_hidden digest__repository-events_hidden');
    if (even_more_events.length === 0) {
      return $(this).parent().hide();
    }
  });
});
