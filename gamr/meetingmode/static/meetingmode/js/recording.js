var start = document.querySelector("#start-meeting");
var stop = document.querySelector('#stop-meeting');
var start_icon = document.querySelector("#start-icon");
var transcript = document.querySelector("#transcript");
var summary_field = document.querySelector("#summary");

window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;

var recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-IN';

const meetingCode = JSON.parse(document.getElementById('meeting-code').textContent);
const author = JSON.parse(document.getElementById('author').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/meeting/'
    + meetingCode
    + '/'
);

chatSocket.onmessage = function(e) {
    //console.log('message', e);
    const data = JSON.parse(e.data);
    console.log(e.data);
    summary_field.innerHTML += data.summary;
    transcript.innerHTML += data.transcript;
    transcript.innerHTML += '<br />';
    
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

function toggleStart(){
    if(start.innerHTML == "Start Meeting" || start.innerHTML == "Resume Meeting")
    {
        start.innerHTML = 'Pause Meeting';
        start_icon.innerHTML = 'pause_presentation';

        recognition.start();


    } else {

        start.innerHTML = 'Resume Meeting';
        start_icon.innerHTML = 'keyboard_voice';

        recognition.stop();

    }
}

start.addEventListener('click', function(){
    toggleStart();
})

stop.addEventListener('click', function(){
    start.disabled = true;
    
    recognition.stop();
    final_transcript = '';
})

var final_transcript = '';
recognition.onresult = function(event) {
    var interim_transcript = '';
    for(var i = event.resultIndex; i < event.results.length; ++i)
    {
        if(event.results[i].isFinal) {
            final_transcript = event.results[i][0].transcript;
            const message = '<b>'+'@' + author + ': ' + '</b>' + final_transcript + '\n';
            //console.log(final_transcript);
            // transcript.innerHTML += final_transcript;
            chatSocket.send(JSON.stringify({
                'transcript': message,
                'raw-transcript':final_transcript,
                'command': 'summarize_transcript'
            }));
        } else {
            interim_transcript += event.results[i][0].transcript;
        }
    }
}
