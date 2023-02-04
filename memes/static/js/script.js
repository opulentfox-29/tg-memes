const socket = new WebSocket('ws://127.0.0.1:8000/ws');

socket.onmessage = function(event) {
  try {
    data = JSON.parse(event.data);
    console.log(data);

    new_post(data);

  } catch (e) {
    console.log('Error:', e.message);
  }
};

try {
    function new_post (data) {
        var scroll = document.getElementById('scroll');

        let code = `
                <div class="card">
            <div class="well text-center">
                <div class="row">
                `
                for (var photo in data['photos']) { console.log(photo); code += `
                   <div class="col-md-6">
                        <img src="data:image/png;base64, ${data['photos'][photo].slice(2, -1)}"
                        alt="inn_logo" class="img-fluid">
                    </div>
                    `
                   }
                   code += `
                </div>
            </div>
            <div class="card-body">
                <p class="card-text">
                    ${data['text'].replaceAll('\n', '<br>')}
                </p>
            </div>
        </div>
        `
        scroll.innerHTML = code + scroll.innerHTML
    }

    function start () {
        socket.send(JSON.stringify({
            status: 'start',
        }));
    }

    btn_start.onclick = start
} catch (error) {console.error(error);}

try {
    function settings_save() {
        var token = document.getElementById('token').value;
        var chat_id = document.getElementById('chat_id').value;
        var chunk_size = document.getElementById('chunk_size').value;
        var cycle = document.getElementById('cycle_checkbox').checked;
        var proxy = document.getElementById('proxy_checkbox').checked;
        var links = document.getElementById('links').value;

        socket.send(JSON.stringify({
            status: 'settings',
            settings: {
                'token': token,
                'chat_id': chat_id,
                'chunk_size': chunk_size,
                'cycle': cycle,
                'dont_use_proxy': proxy,
                'links': links,
            }
        }));

        alert('saved');
    }
    btn_save.onclick = settings_save
} catch (error) {console.error(error);}
