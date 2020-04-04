const socket = io.connect(window.location.host);
socket.emit("join_user_to_room", r_id); //Join request to this socket.oi's room

const user_url = $("#room_user_url"),
    section_questions = $(".questions"),
    section_metadata = $(".metadata"),
    discard_q = $(".dont_add_question"),
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

    // Set the questions section's height to fit the window size:
    section_questions.css("height", $(window).height() - section_metadata.outerHeight() + "px");

    // Room lifetime setup
    startTimer(expiry_duration, room_lifetime_p);
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
    )
})

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
    .append($('<h3 class="total_votes">Total Hums: 0</h3>'))
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
    options_wrapper.append('<button class="place_vote_btn" onclick="send_hums(this)">Hum Now</button>');

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
    socket.emit("new_hum", {r_id: r_id, q_id: q_id, "vote": votes});
}


socket.on("hum_update", function(data) {
    total_votes_h = $(".total_votes");
    total_votes_h.text("Total Number of Hums: " + data.num_users_voted);
})

socket.on("room_closed", function(data) {
    // Close room
    
    console.log("Room closed");
    location.href = location.origin;
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