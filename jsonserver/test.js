const http = require('http');
const socketio = require('socket.io');
const fs = require('fs');

// Create the HTTP server
const server = http.createServer((req, res) => {
  // Serve the HTML file
  if (req.url === '/') {
    fs.readFile('index.html', (err, data) => {
      if (err) {
        res.writeHead(500);
        return res.end('Error loading index.html');
      }
      res.writeHead(200);
      res.end(data);
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

// Create the Socket.io server
const io = socketio(server);

io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('json', (json_data) => {
    console.log(`Received JSON data: ${json_data}`);
    // Send the JSON data to the client.py script
    io.emit('json', json_data);

    // Wait for response from client.py
    socket.once('result', (result) => {
      console.log(`Received result from client.py: ${result}`);
    });
  });
});

// Start the server
const PORT = 3001;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));