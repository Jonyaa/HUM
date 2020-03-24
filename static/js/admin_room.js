const socket = io.connect(window.location.host);
socket.emit("join_user_to_room", r_id); //Join request to this socket.oi's room

const user_url = $("#room_user_url"),
    admin_url = $("#room_admin_url"),
    section_questions = $(".questions"),
    section_metadata = $(".metadata"),
    add_q_btn = $("#add_question"),
    discard_q = $(".dont_add_question"),
    q_form = $(".add_question_form_wrap"),
    add_form = $(".add_question_form"),
    pending_wrap = $(".pending_questions_wrap"),
    pending_q = $(".pending_question"),
    total_connected_p = $("#total_connected"),
    total_uniqe_ip_p = $("#total_unique_ips"),
    room_lifetime_p = $("#room_lifetime");

socket.on('user_status_update', function(data){
    total_connected_p.text(data["total_connections"]);
    total_uniqe_ip_p.text(data["num_of_uniqe_ip"]);
});

window.addEventListener("beforeunload", function () {
    socket.emit('disconnecting', r_id);
})

function startTimer(duration, display) {
    var timer = duration, hours, minutes, seconds;
    setInterval(function () {
        hours = parseInt(timer / 3600, 10);
        minutes = parseInt((timer / 60) % 60, 10);
        seconds = parseInt(timer % 60, 10);

        hours = hours < 10 ? "0" + hours : hours;
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.text( hours + ":" + minutes + ":" + seconds);

        if (--timer < 0) {
            timer = duration;
        }
    }, 1000);
}

$(document).ready(function() {

    // Set URL at metadata section
    user_url.html(location.origin + "/room/" + user_url.html());
    admin_url.html(location.href);

    // Set the questions section's height to fit the window size:
    section_questions.css("height", $(window).height() - section_metadata.outerHeight() + "px");

    // Room lifetime setup
    console.log(expiry_duration)
    startTimer(expiry_duration, room_lifetime_p);
})


add_q_btn.click(function() {
    q_form.toggleClass("show");
})
discard_q.click(function() {
    q_form.toggleClass("show");
})


function add_question(event) {
    // The functions that runs whenever one clicks the "add question" button
    event.preventDefault();

    let q = $("input[name=question").val();
    let options = [];
    $("input[name=option]").each(function() {
        // Get the filled options from the form and put them inside the options array
        if ($(this).val() != "") {
            options.push($(this).val());
        }
    });

    $(".add_question_form input[type=text]").each(function() {
        $(this).val("");
    })

    socket.emit("admin_new_question", {r_id: r_id, q_id: $(".pending_question").length, question: q, desc: "test", options: options});
    // THIS JQUERY ADDS THE NEW DOM QUESTION DIV'S ELEMENTS TO THE PENDING QUESTIONS AREA
    pending_wrap.append($("<div class='pending_question' id='q"+$(".pending_question").length+"'></div>")
        .append($("<h3 class='question'>"+q+"</h3>"))
        .append($("<div class='pending_question_options'></div>")
            .append(function() {
                let res = "";
                $(options).each(function(index, element) {
                    res += "<h5 class='option'>"+(index+1) + ". " + this + "</h5>";
                });
                return res;
            }))
        .append($("<img src='../static/img/svg/next2.svg' class='next_add_question'>"))
        .append($("<img src='../static/img/svg/trash.svg' class='trash_question'>"))
    )
    
    q_form.toggleClass("show");

}

socket.on("new_question_update", function(data) {
    alert("NEW QUESTION UPDATE!");
})