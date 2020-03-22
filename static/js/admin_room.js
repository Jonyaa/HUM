const socket = io.connect(window.location.host);
socket.emit("join_user_to_room", r_id); //Join request to this socket.oi's room

socket.on('user_status_update', function(data){
    console.log(data);
});

window.addEventListener("beforeunload", function () {
    socket.emit('disconnecting', r_id);
})