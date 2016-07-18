$(function(){
  var zmq = require('zmq');

  function connectToServer(conn){
    // need to add modules to the path manually
    console.log("testing that I can write to console.");

    // load zmq, start with simple client example
    console.log("Connecting to hello world server...");
    conn.requester = zmq.socket('req');

    var x=0;
    conn.requester.on("message", function(reply){
      respText = 'Received reply '+ x.toString() + ': [' + reply.toString() + ']';
      console.log(respText);
      x += 1;
      $('#data').text(respText);
      if (x === 10) {
        conn.requester.close();
  //      process.exit(0); // TODO: Do I need this?
      }
    });

    url = 'tcp://' + conn.server.toString() + ':' + conn.port.toString();
    console.log('Server at: ', url);
    conn.requester.connect(url);

    for (var i = 0; i < 10; i++){
      console.log('Sending request', i, '...');
      conn.requester.send("Hello");
    }

    process.on('SIGINT', function() {
      console.log('am I closing here');
      conn.requester.close();
    });
  }

  var conn = {
    server: 'localhost',
    port: 5555
  };
  connectToServer(conn);
});
