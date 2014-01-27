// When the DOM is ready, run this function
$(document).ready(function() {
  //Set the carousel options
  $('#quote-carousel').carousel({
    pause: true,
    interval: 4000,
  });
});

function delRequest(request) {
    var field = document.getElementById('del-' + request);
    hideDiv('content-'+request);
    field.innerHTML = '<div class="alert alert-danger alert-dismissable">' + 
                        '<button type="button" class="close" onclick="showRequest('+request+')">&times;</button>' +
                        '<strong>Warning!</strong> Are you sure you would like to remove request <strong>'+request+'</strong>?' +
                        '<center>' +
                            '<div class="btn-group" style="padding-top: 20px;">' +
                              '<a type="button" class="btn btn-danger" href="/request?delete='+request+'">Delete</a>' +
                              '<button type="button" class="btn btn-default" onclick="showRequest('+request+')">Cancel</button>' +
                            '</div>' +
                        '</center>' +
                      '</div>';
};

function showRequest(request) {
    var field = document.getElementById('del-' + request);
    field.innerHTML = '';
    showDiv('content-'+request)
};

function showDiv(toggle){
document.getElementById(toggle).style.display = 'block';
};

function hideDiv(toggle){
document.getElementById(toggle).style.display = 'none';
};