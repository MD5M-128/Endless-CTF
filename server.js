const WebSocket = require('ws');

const wss = new WebSocket.Server({port: 8765});

wss.on('connection', function connection(ws, req) {
	console.log("Client connected.");
	ws.on('message', function incoming(message) {
		var msg = JSON.parse(message);
		console.log("< " + message);
		var packet = {
			"time": Date.now(),
			"content": msg["content"],
			"fromIp": req.connection.remoteAddress,
			"toIp": msg["ip"],
			"fromPort": req.connection.remotePort,
			"toPort": msg["port"]
		};
		wss.clients.forEach(function each(client) {
			if (client !== ws && client.readyState === WebSocket.OPEN) {
				client.send(JSON.stringify(packet));
			}
		});
	});
  });