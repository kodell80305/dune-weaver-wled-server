echo "Patching index.html 2"
mkdir -p templates
mkdir -p static/styles
mkdir -p static/js
cp ../WLED/wled00/data/index.css static/styles
cp ../WLED/wled00/data/iro.js static/js
cp ../WLED/wled00/data/rangetouch.js static/js
cp ../WLED/wled00/data/common.js static/js
cp ../WLED/wled00/data/404.htm templates 

#<button id="buttonSr" onclick="toggleLiveview()"><i class="icons">&#xe410;</i><p class="tab-label">Peek</p></button>
#sed "s/toggleLiveView()\"/toggleLiveView()\" hidden/g" |
cat  ../../WLED/wled00/data/index.htm | sed "s/index\.css/ {{ url_for('static', filename='styles\/index.css') }}/g" | 
sed "s/rangetouch\.js/{{ url_for('static', filename='js\/rangetouch.js') }}/g" |
sed "s/common\.js/{{ url_for('static', filename='js\/common.js') }}/g" |
sed "s/index\.js/{{ url_for('static', filename='js\/index.js') }}/g"  |
sed "s/toggleLiveview()\"/toggleLiveview()\" hidden/g" |
sed "s/toggleSync()\"/toggleSync()\" hidden/g" |
sed "s/settings');./settings');\" hidden/g" | 
sed "s/iro\.js/{{ url_for('static', filename='js\/iro.js') }}/g" > templates/index.htm
#index.js wants websocket ... let's create a fake web socket class


insert_stub=$(cat <<EOF
class StubWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = StubWebSocket.CONNECTING;
    this.sentMessages = [];
    
    // Simulate connection opening after a short delay
    setTimeout(() => {
      this.readyState = StubWebSocket.OPEN;
      if (this.onopen) {
        this.onopen();
      }
    }, 10); 
  }

  send(data) {
    this.sentMessages.push(data);
    if (this.onmessage) {
      this.onmessage({ data: data });
    }
  }

  close() {
    this.readyState = StubWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose();
    }
  }

  onopen() {
    console.log('Connected to WebSocket server');
    this.send('Hello, server!');
  }

  onmessage(event) {
    console.log('Received message:', event.data);
  } 

  onwerror(error) {
    console.error('WebSocket error:', error);
  }

  onclose () {
    console.log('Disconnected from WebSocket server');
  }
  
  simulateMessage(data) {
      if (this.onmessage) {
          this.onmessage({ data: data });
      }
  }
}

StubWebSocket.CONNECTING = 0;
StubWebSocket.OPEN = 1;
StubWebSocket.CLOSING = 2;
StubWebSocket.CLOSED = 3;
EOF
)

#last is ugly hack, my brain is too tired to deal with sed right now ..
#sed 's/if (!s) return false/return false/' >> static/js/index.js
echo "$insert_stub"  > static/js/index.js
cat ../../WLED/wled00/data/index.js |
sed "s/WebSocket/StubWebSocket/g" |
sed "s/var useWs = (ws && ws.readyState === StubWebSocket.OPEN);/var useWs = false/" >> static/js/index.js
cat ../../WLED/wled00/data/settings.htm |
sed "s/common\.js/{{ url_for('static', filename='js\/common.js') }}/g" >> templates/settings.htm

echo DONE



 
