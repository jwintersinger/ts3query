$(document).ready(function() {
  $('.client-details').hide();
  $('.client').mouseenter(function() {
    $(this).find('.client-details').show();
  }).mouseleave(function() {
    $(this).find('.client-details').hide();
  });
});
