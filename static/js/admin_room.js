//const socket = io.connect(window.location.host);
const user_url = $("#room_user_url"),
    admin_url = $("#room_admin_url"),
    section_questions = $(".questions"),
    section_metadata = $(".metadata"),
    add_q_btn = $("#add_question"),
    discard_q = $(".dont_add_question"),
    q_form = $(".add_question_form_wrap"),
    add_form = $(".add_question_form"),
    pending_wrap = $(".pending_questions_wrap"),
    pending_q = $(".pending_question");


$(document).ready(function() {

    // Set URL at metadata section
    user_url.html(location.origin + "/room/" + user_url.html());
    admin_url.html(location.href);

    // Set the questions section's height to fit the window size:
    section_questions.css("height", $(window).height() - section_metadata.outerHeight() + "px");
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