function publicComment(comment){
    var cookie = getCookie('session_id');
    var comment_time = comment.id;
    var xmlhttp=new XMLHttpRequest();
    xmlhttp.open("POST","/api/v1/comment/public",true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send("cookie="+cookie+"&created_at="+comment_time);
}

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}
