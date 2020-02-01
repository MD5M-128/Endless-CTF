const WebSocket = require('ws');

const wss = new WebSocket.Server({port: 8765});

var allDNS = [];
var dnsCreds = {
	"hello.com": {
		"desc": "Hello, world!",
		"owner": {
			"name": "Me",
			"email": "me@hello.com"
		},
		"password": "hi"
	}
};

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
				"toIp": msg["ip"],
				"fromPort": req.connection.remotePort,
				"toPort": msg["port"]
			};
			wss.clients.forEach(function each(client) {
				if (client.readyState === WebSocket.OPEN) {
					client.send(JSON.stringify(packet));
				}
			});
		} else if (msg.type == "dns_login") {
			if (msg.name in dnsCreds) {
				var packet = {
					"type": "dns_login",
					"time": Date.now(),
					"ip": ipv4_to_num(req.connection.remoteAddress),
					"name": msg.name,
					"desc": dnsCreds[msg.name].desc,
					"owner": dnsCreds[msg.name].owner
				};
				if (msg.password == dnsCreds[msg.name].password) {
					allDNS.push(packet);
					wss.clients.forEach(function each(client) {
						if (client.readyState === WebSocket.OPEN) {
							client.send(JSON.stringify(packet));
						}
					});
				}
			}
		} else if (msg.type == "dns_all") {
			var packet = {
				"type": "dns_all",
				"entries": allDNS
			};
		}
	})
});