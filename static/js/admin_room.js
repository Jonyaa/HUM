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

var current_deleting_question = null;

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

        // Display second only if less than hour left
        if (duration < 3600){
            display.text( minutes + ":" + seconds);
        } else {
            display.text( hours + ":" + minutes);
        }

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
    startTimer(expiry_duration, room_lifetime_p);
})


add_q_btn.click(function() {
    q_form.toggleClass("show");
    console.log(add_form.children(".form_options").children().last());
    add_form.children(".form_options").children().last().val("I don't have enough information.");
})
discard_q.click(function() {
    q_form.toggleClass("show");
})
document.addEventListener("keydown", function (e) {
    if (e.keyCode == 27 && q_form.hasClass("show")) {
        q_form.toggleClass("show");
    }
})


function download_json(event){
    // This function sends a request to the JSON file and downloads it
    socket.emit("get_json", {r_id: r_id});
    socket.on("json_recived", function(data) {
        var file_name = data.file_name;
        var file_url = location.origin + "\\" + file_name;
        window.open(file_url, '_blank');
    })

}

function close_room() {
    $("#close_alert").toggleClass("show");
}

function yes_really(){
    // This function send the server closing request and when it gets a confirmation message 
    //    it redicts the user the main screen

    admin_r_id = location.href.split("/").slice(-1); 
    socket.emit("close_room", {r_id: r_id, admin_r_id: admin_r_id[0]});
    
    socket.on("room_closed", function(data) {
        console.log("Room closed");
        location.href = location.origin;
    })
}

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

    socket.emit("admin_new_question", {r_id: r_id, q_id: "q"+this_question_id, question: q, desc: "test", options: options});
    
    this_question_id += 1;
    q_form.toggleClass("show");
}

socket.on("new_question_update", function(data) {
    // THIS JQUERY ADDS THE NEW DOM QUESTION DIV'S ELEMENTS TO THE PENDING QUESTIONS AREA
    var q_id = data.q_id, q = data.question, options = data.options, desc = data.desc;
    pending_wrap.append($("<div class='pending_question' id="+q_id+"></div>")
        .append($("<h3 class='question'>"+q+"</h3>"))
        .append($("<div class='pending_question_options'></div>")
            .append(function() {
                let res = "";
                $(options).each(function(index, element) {
                    res += "<h5 class='option'>"+(index+1) + ". " + this + "</h5>";
                });
                return res;
            }))
        .append($("<img src='../static/img/svg/next.svg' class='next_add_question' onclick='put_on_vote(this)' title='Put on vote' alt='Put on vote'>"))
        .append($("<img alt='Delete question' title='Delete question' src='../static/img/svg/trash.svg' class='trash_question' onclick='pop_delete_question(this)'>"))
    )
})


function put_on_vote(e) {
    console.log($(".on_vote_question").children());
    if ($(".on_vote_question").children().length != 0) {
        alert("Please wait until voting will finish");
    } else {
        var q_id = e.parentNode.id;
        socket.emit("admin_published_question", {r_id: r_id, q_id: q_id});
    }
}

function cancel_deletion() {
    $("#delete_alert").toggleClass("show");
}

function pop_delete_question(question) {
    current_deleting_question = question.parentNode.id;
    console.log(current_deleting_question);
    $("#delete_alert").toggleClass("show");
    $("#delete_question_placeholder").html($(question).parent().children(".question").html());
}

function delete_question(obj, e) {
    obj.parentElement.classList.toggle("show");
    socket.emit("admin_deleted_question", {r_id: r_id, q_id: current_deleting_question});
}

socket.on("question_deleted", function(data) {
    var q_id = data.q_id;
    question_div = $("#"+q_id+".pending_question");
    question_div.remove()
});


socket.on("voting_started", function(data) {
    var q_id = data.q_id,
        q = data.question,
        options = data.options,
        vote_expiry_duration = data.expiry_duration
    
    $('.on_vote_question')
    .append($('<h3 class="question" id='+q_id+'>'+q+'</h3>'))
    .append($('<h3 class="total_votes">TOTAL HUMS: <span id="total_votes_span">0</span></h3>'))
    .append($('<h3 class="vote_timer"></h3>'));

    // Voting timer
    vote_timer = $(".vote_timer");
    startTimer(vote_expiry_duration, vote_timer);

    $(".pending_question#"+q_id).remove();

    // Create options form
    
    var options_wrapper = $("<div class='options_wrapper'></div>")
    $('.on_vote_question').append(options_wrapper)

    // Create button for each option
    for (var option_key in options) {
        options_wrapper.append($('<label class="vote_option_container"></label>')
                    .append($('<input type="checkbox" name='+option_key+'>'))
                    .append($('<span class="checkmark"></span>'))
                    .append($('<p class="option_label">'+options[option_key]+'</p>')))
    }
    options_wrapper.append('<button class="place_vote_btn" onclick="send_hums(this)">SEND VOTE</button>');

})

function send_hums(obj) {
    var q_id = obj.parentElement.parentElement.children[0].id;
    var votes = "";
    $("input[type=checkbox]").each(function() {
        if (this.checked) {
            votes += "1";
        } else {
            votes += "0";
        }
    })
    if (votes.length < 4) {
        var n = 4-votes.length;
        for (let i = 0; i < n; i++) {
            votes += "0";
        }
    }
    obj.parentElement.remove();
    console.log(q_id + "-" + votes);
    socket.emit("new_hum", {r_id: r_id, q_id: q_id, "vote": votes});
}


socket.on("hum_update", function(data) {
    total_votes_h = $("#total_votes_span");
    total_votes_h.text(data.num_users_voted);
})

socket.on("humming_finished", function(data) {
    // After huuming (voting) the server sends the results and this function display the results 
    //      and reset "on vote" section 
    var q_id = data.q_id,
    q = data.question,
    options = data.options,
    results = data.results
    $('#finished_voting')
    .append($('<div class="finished_question" id='+q_id+'></div>'))
    finished_question_div = $('#'+q_id+'.finished_question');
    finished_question_div
        .append($('<h3 class="question">'+q+'</h3>'))
    
    // For item in options dictionary: print option + result
    for (var option_key in options){
        finished_question_div
            .append($('<h3 class="finished_option">'+options[option_key]+' - <span class="option_hum">'+results[parseInt(option_key)]+'</span></h3>'))
    }

    // Remove question from voting section
    $(".question#"+q_id).remove();
    $(".total_votes").remove();
    $(".vote_timer").remove();
    $(".humming_form").remove();
    $(".options_wrapper").remove();
            
})


// The function that copies the user url to clipboard
function copy_url(element, event) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
    var x = event.pageX, y = event.pageY;
    $("#copy_alert").css({"left": x+15+'px', "top": y-15+"px"}).fadeIn(200).delay(1000).fadeOut(200);
  }

