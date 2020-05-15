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

var SpeechGrammarList = SpeechGrammarList || webkitSpeechGrammarList;
var grammar = '#JSGF V1.0;'
var speechRecognitionList = new SpeechGrammarList();
speechRecognitionList.addFromString(grammar, 1);
recognition.grammars = speechRecognitionList;


const meetingCode = JSON.parse(document.getElementById('meeting-code').textContent);
const author = JSON.parse(document.getElementById('author').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/meeting/'
    + meetingCode
    + '/'
);

chatSocket.onopen = function(e) {
    chatSocket.send(JSON.stringify({
        'command': 'fetch_meeting_info'
    }));

}

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    summary_field.innerHTML = '';
    console.log(e.data);
    transcript.innerHTML += data.transcript;
    summary_field.innerHTML += data.summary;
    chatSocket.send(JSON.stringify({
        'command': 'save_meeting_info',
        'final_transcript':transcript.innerHTML,
        'final_summary':summary_field.innerHTML
    }));
    
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

    console.log(final_transcript);
    chatSocket.send(JSON.stringify({
        'command': 'save_meeting_info',
        'final_transcript':transcript.innerHTML,
        'final_summary':summary_field.innerHTML
    }));

})

var final_transcript = '';
recognition.onresult = function(event) {
    var interim_transcript = '';
    for(var i = event.resultIndex; i < event.results.length; ++i)
    {
        if(event.results[i].isFinal) {
            final_transcript = event.results[i][0].transcript;
            // console.log(final_transcript);
            // const message = '<b>'+'@' + author + ': ' + '</b>' + final_transcript + '\n';
            // transcript.innerHTML += message;
            // transcript.innerHTML += '<br />';
            //console.log(final_transcript);
            // transcript.innerHTML += final_transcript;
            // console.log(chatSocket.readyState)
            chatSocket.send(JSON.stringify({
                'raw-transcript':final_transcript,
                'command': 'summarize_transcript',
                'author':author
            }));
        } else {
            interim_transcript += event.results[i][0].transcript;
            console.log(interim_transcript);
        }
    }
}
