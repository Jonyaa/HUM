const socket = io.connect(window.location.host);
const r_number = location.pathname.split("/").slice(-1)

function join_room(){
    socket.emit("join_admin_room", r_number);
    return false;
};

window.addEventListener("beforeunload", function () {
    socket.emit('disconnecting');
})