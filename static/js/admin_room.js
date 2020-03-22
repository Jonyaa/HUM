//const socket = io.connect(window.location.host);
const user_url = document.getElementById("room_user_url"),
    admin_url = document.getElementById("room_admin_url"),
    section_questions = document.getElementsByClassName("questions")[0];

user_url.innerHTML = location.origin + "/room/" + user_url.innerHTML;
admin_url.innerHTML = location.href;

document.getElementsByClassName("questions")[0].style.height = window.innerHeight - document.getElementsByClassName("metadata")[0].offsetHeight + "px"