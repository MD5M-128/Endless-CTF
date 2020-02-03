var webSocket;

// Source: https://gist.github.com/jppommet/5708697
function num_to_ipv4(ipInt) {
    return ( (ipInt >>> 24) + '.' + (ipInt >> 16 & 255) + '.' + (ipInt >> 8 & 255) + '.' + (ipInt & 255) );
}
function ipv4_to_num(ip) {
    return ip.split('.').reduce(function(ipInt, octet) { return (ipInt << 8) + parseInt(octet, 10)}, 0) >>> 0;
}

function connect() {
    var table = document.getElementById("packets");
    var dnsTable = document.getElementById("dns");
    webSocket = new WebSocket("ws://" + window.location.hostname + ":8765");
    webSocket.onmessage = function(event) {
        var msg = JSON.parse(event.data);
        if (msg.type == "packet" && table) {
            var row = document.createElement("tr");
            for (var i = 0; i < 6; i++) {
                row.appendChild(document.createElement("td"));
            }
            ipLinkA = document.createElement("a");
            ipLinkB = document.createElement("a");
            ipLinkA.setAttribute("href", "/dns#" + num_to_ipv4(msg.fromIp));
            ipLinkB.setAttribute("href", "/dns#" + num_to_ipv4(msg.ip));
            row.childNodes[0].appendChild(ipLinkA);
            row.childNodes[1].appendChild(ipLinkB);
            row.childNodes[0].firstChild.textContent = num_to_ipv4(msg.fromIp);
            row.childNodes[1].firstChild.textContent = num_to_ipv4(msg.ip);
            row.childNodes[2].textContent = msg.fromPort.toString();
            row.childNodes[3].textContent = msg.port.toString();
            row.childNodes[4].textContent = msg.content;
            row.childNodes[5].textContent = msg.time.toString();
            table.appendChild(row);
        } else if (msg.type == "dns_login" && dnsTable) {
            var existed = true;
            var nameRow = document.getElementById(msg.name);
            if (!nameRow) {
                nameRow = document.createElement("tr");
                nameRow.id = msg.name;
                existed = false;
                for (var i = 0; i < 5; i++) {
                    nameRow.appendChild(document.createElement("td"));
                }
            }
            nameRow.childNodes[0].textContent = num_to_ipv4(msg.ip);
            nameRow.childNodes[0].id = num_to_ipv4(msg.ip);
            nameRow.childNodes[1].textContent = msg.name;
            nameRow.childNodes[2].textContent = msg.owner.name;
            nameRow.childNodes[3].textContent = msg.desc;
            nameRow.childNodes[4].textContent = msg.time.toString();
            if (!existed) {
                dnsTable.appendChild(nameRow);
            }
        } else if (msg.type == "dns_logout" && dnsTable) {
            var nameRow = document.getElementById(msg.name);
            if (nameRow) {
                dnsTable.removeChild(nameRow);
            }
        } else if (msg.type == "dns_all" && dnsTable) {
            msg.entries.forEach(function(ent) {
                var existed = true;
                var nameRow = document.getElementById(ent.name);
                if (!nameRow) {
                    nameRow = document.createElement("tr");
                    nameRow.id = ent.name;
                    existed = false;
                    for (var i = 0; i < 5; i++) {
                        nameRow.appendChild(document.createElement("td"));
                    }
                }
                nameRow.childNodes[0].textContent = num_to_ipv4(ent.ip);
                nameRow.childNodes[0].id = num_to_ipv4(msg.ip);
                nameRow.childNodes[1].textContent = ent.name;
                nameRow.childNodes[2].textContent = ent.owner.name;
                nameRow.childNodes[3].textContent = ent.desc;
                nameRow.childNodes[4].textContent = ent.time.toString();
                if (!existed) {
                    dnsTable.appendChild(nameRow);
                }
            });
        }
    };
    webSocket.onopen = function(event) {
        loadDNS();
    }
}

function loadDNS() {
    webSocket.send('{"type": "dns_all"}');
}