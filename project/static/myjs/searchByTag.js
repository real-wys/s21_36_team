$(document).on('click','button',function (e) {
    var key = this.innerText;
    var url="/searchByTag/?tag="+key;
    location.href = url;

})