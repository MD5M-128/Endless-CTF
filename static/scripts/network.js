var webSocket;

function connect() {
    var table = document.getElementById("packets");
    webSocket = new WebSocket("ws://" + window.location.hostname + ":8765");
    webSocket.onmessage = function(event) {
        var msg = JSON.parse(event.data);
        var row = document.createElement("tr");
        for (var i = 0; i < 6; i++) {
            row.appendChild(document.createElement("td"));
        }
        row.childNodes[0].textContent = msg.fromIp;
        row.childNodes[1].textContent = msg.toIp;
        row.childNodes[2].textContent = msg.fromPort.toString();
        row.childNodes[3].textContent = msg.toPort.toString();
        row.childNodes[4].textContent = msg.content;
        row.childNodes[5].textContent = msg.time.toString();
        table.appendChild(row);
    };
}