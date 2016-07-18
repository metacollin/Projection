const electron = require('electron')
// Module to control application life.
const app = electron.app
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow

var zmq = require('zmq');

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({width: 800, height: 600})

  // and load the index.html of the app.
  mainWindow.loadURL(`file://${__dirname}/index.html`)

  // Open the DevTools.
  mainWindow.webContents.openDevTools()

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })

  var conn = {
    server: 'localhost',
    port: 5555
  };
  connectToServer(conn);
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

function connectToServer(conn){
  // need to add modules to the path manually
  console.log("testing that I can write to console.");

  // load zmq, start with simple client example
  console.log("Connecting to hello world server...");
  conn.requester = zmq.socket('req');

  var x=0;
  conn.requester.on("message", function(reply){
    console.log('Received reply', x, ': [', reply.toString(), ']');
    x += 1;
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
