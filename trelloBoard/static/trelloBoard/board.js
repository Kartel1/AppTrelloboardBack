$('#dropdown-organizations li').on('click', function (event){
    var $selectedItem = $(this).index();
    if($selectedItem > 0){
      $('#dropdown-boards').show();
      $('#dropdown-sprints').show();
    }else{
     $('#dropdown-boards').hide();
     $('#dropdown-sprints').hide();
    }
});
