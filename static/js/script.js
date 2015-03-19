function publicComment(comment) {
    var comment_time = comment.id;
    var post_title = comment.name;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/api/v1/comment/public", true);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4) {
            if (xmlhttp.status == 200) {
                var response = JSON.parse(xmlhttp.responseText);
                changePublicStatus(response, comment);
            }
            else {
                console.log('Network problem')
            }
        }
    };
    xmlhttp.send("post_title=" + post_title + "&created_at=" + comment_time);
}

function changePublicStatus(response, comment) {
    var status = response['status'];
    if (status == 'success') {
        if (comment.value == 'Public') {
            comment.value = 'Un-public'
        }
        else {
            comment.value = 'Public'
        }
    }
    else {
        console.log('Failed auth')
    }
}