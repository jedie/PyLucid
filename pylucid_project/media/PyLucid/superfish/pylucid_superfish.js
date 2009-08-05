$(document).ready(function(){
  //
  // initialise Superfish menu
  // 
  $('ul.sf-menu').superfish({ 
      delay:       0,                               // delay on mouseout 
      animation:   {opacity:'show',height:'show'},  // fade-in and slide-down animation 
      speed:       'fast'                           // faster animation speed
  });
});