$('#refresh-button').on('click', function(event){
    event.preventDefault();
    var $thisURL = $('#refresh-button').attr('data-url')
    console.log("button clicked!")  // sanity check
    update_board($thisURL);
    $('#refresh-button').blur();
});

function update_board(url) {
    $.ajax({
      method: "POST",
      url: url,
      success: function(data) {
        console.log(data) // check out how data is structured
        alert("Mise à jour réussie");
      },
      error: function(data){
        console.log(data)
        alert("Echec mise à jour , Veuillez vous reconnecter à Trello");
      }
    })
  };






  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});