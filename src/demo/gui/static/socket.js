const socket = io();

function updateSliderValue(id) {
    const slider = document.getElementById(id);
    document.getElementById(id + "Value").textContent = slider.value;
}

function adjustConfig() {
    const geoQP = parseInt(document.getElementById("geoQP").value);
    const attQP = parseInt(document.getElementById("attQP").value);
    const sequence = document.getElementById("sequence").value;

    socket.emit("adjust_config", { sequence, geoQP, attQP });
}
