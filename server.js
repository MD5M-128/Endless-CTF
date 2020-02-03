const WebSocket = require('ws');
const bcrypt = require('bcrypt');
const fs = require("fs");

// P@55W0RD
// Sandwich
// MoyesIsRed
// DUCKSDUCKSDUCKS

const wss = new WebSocket.Server({port: 8765});

var allDNS = [];
var dnsCreds = JSON.parse(fs.readFileSync("dnsrecords.json"));

// Source: https://gist.github.com/jppommet/5708697
function num_to_ipv4(ipInt) {
    return ( (ipInt >>> 24) + '.' + (ipInt >> 16 & 255) + '.' + (ipInt >> 8 & 255) + '.' + (ipInt & 255) );
}
function ipv4_to_num(ip) {
    return ip.split('.').reduce(function(ipInt, octet) { return (ipInt << 8) + parseInt(octet, 10)}, 0) >>> 0;
}

wss.on('connection', function connection(ws, req) {
	console.log("Client connected.");
	ws.on('message', function incoming(message) {
		var msg = JSON.parse(message);
		console.log("< " + message);
		if (msg.type == "packet") {
			var packet = {
				"type": "packet",
				"time": Date.now(),
				"content": msg["content"],
				"fromIp": ipv4_to_num(req.connection.remoteAddress),
				"ip": msg["ip"],
				"fromPort": req.connection.remotePort,
				"port": msg["port"]
			};
			wss.clients.forEach(function(client) {
				if (client.readyState === WebSocket.OPEN) {
					client.send(JSON.stringify(packet));
				}
			});
		} else if (msg.type == "dns_login") {
			if (msg.domain in dnsCreds) {
				var packet = {
					"type": "dns_login",
					"time": Date.now(),
					"ip": ipv4_to_num(req.connection.remoteAddress),
					"server": msg.server,
					"domain": msg.domain,
					"name": msg.server + "." + msg.domain,
					"desc": dnsCreds[msg.domain].desc,
					"owner": dnsCreds[msg.domain].owner
				};
				if (bcrypt.compareSync(msg.password, dnsCreds[msg.domain].password)) {
					allDNS.push(packet);
					wss.clients.forEach(function(client) {
						if (client.readyState === WebSocket.OPEN) {
							client.send(JSON.stringify(packet));
						}
					});
				} else {
					ws.send('{"type": "dns_badpassword"}');
				}
			} else {
				ws.send('{"type": "dns_notregistered"}');
			}
		} else if (msg.type == "dns_logout") {
			var entry = null;
			var entryI = null;
			var fullName = msg.server + "." + msg.domain;
			for (var i = allDNS.length - 1; i >= 0; i--) {
				if (allDNS[i].name == fullName) {
					entry = allDNS[i].name;
					entryI = i;
				}
			}
			if (entry) {
				if (bcrypt.compareSync(msg.password, dnsCreds[msg.domain].password)) {
					allDNS.splice(entryI, 1);
					var packet = {
						"type": "dns_logout",
						"name": entry.name
					};
					wss.clients.forEach(function(client) {
						if (client.readyState === WebSocket.OPEN) {
							client.send(JSON.stringify(packet));
						}
					});
				} else {
					ws.send('{"type": "dns_badpassword"}');
				}
			} else {
				ws.send('{"type": "dns_notloggedin"}');
			}
		} else if (msg.type == "dns_all") {
			var packet = {
				"type": "dns_all",
				"entries": allDNS
			};
			ws.send(JSON.stringify(packet));
		} else if (msg.type == "dns_lookup") {
			var entry = null;
			for (var i = allDNS.length - 1; i >= 0; i--) {
				if (allDNS[i].name == msg.name) {
					entry = allDNS[i];
				}
			}
			if (entry) {
				entry.type = "dns_result";
				ws.send(JSON.stringify(entry));
			} else {
				ws.send('{"type": "dns_notfound"}');
			}
		}
	})
});