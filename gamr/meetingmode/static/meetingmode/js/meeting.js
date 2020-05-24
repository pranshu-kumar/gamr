var start = document.querySelector("#start-meeting");
var stop = document.querySelector('#stop-meeting');
var start_icon = document.querySelector("#start-icon");
var transcript = document.querySelector("#transcript");
var summary_field = document.querySelector("#summary");

var i = 0;

var add_task = document.getElementById('add'+i+'-task');
var task_text = document.querySelector('#task'+i+'-text');
var tbody = document.querySelector('#tbody');


/************************ Translate ***********************************/
function translateTo(id){

    // console.log(summary_field.innerHTML);
    // console.log(summary_field.textContent);

    chatSocket.send(JSON.stringify({
        'command': 'translate_summary',
        'final_summary':summary_field.textContent,
        'translate_to':id
    }));
    
}


/************************ Adding Tasks ***********************************/
function addTasktoDatabase(){

   
    var task = document.createElement('h5');
    task.setAttribute('class', 'text-center')
    task.innerHTML = task_text.value;
    task_text.parentNode.appendChild(task);
    task_text.parentNode.removeChild(task_text);

    var removeIcon = document.createElement("button");
    removeIcon.setAttribute('id', 'remove'+i+'-task');
    removeIcon.setAttribute('title', 'Remove Task');
    removeIcon.setAttribute('class', 'btn btn-white btn-link btn-lg');
    removeIcon.setAttribute('onclick', 'removeTaskfromDatabase(this.id)')
    
    var icon = document.createElement('i');
    icon.setAttribute('class', 'material-icons');
    icon.innerHTML = 'close';

    removeIcon.appendChild(icon);
    add_task.parentNode.appendChild(removeIcon);
    add_task.parentNode.removeChild(add_task);
    i = i+1;
    add_field();

};

function removeTaskfromDatabase(id){
    var el = document.getElementById(id);
    var td1 = el.parentNode;
    var tr1 = td1.parentNode;
    tr1.parentNode.removeChild(tr1);
}

function add_field() {
  
    
    var textid = 'task'+i+'-text';
    var buttonId = 'add'+i+'-task';

    var tr = document.createElement('tr');
    tr.setAttribute('id', 'tr'+i+'_id');
    var td1 = document.createElement('td');
    var div = document.createElement('div');
    div.setAttribute('class', 'form-check');
    var label = document.createElement('label');
    label.setAttribute('class', 'form-check-label');
    var checkbox = document.createElement('input');
    checkbox.setAttribute('class', 'form-check-input');
    checkbox.setAttribute('type', 'checkbox');
    var span1 = document.createElement('span');
    var span2 = document.createElement('span');
    span1.setAttribute('class', 'form-check-sign');
    span2.setAttribute('class', 'check');
    div.appendChild(label)
    label.appendChild(checkbox);
    label.appendChild(span1);
    span1.appendChild(span2);
    td1.appendChild(div);

    var td2 = document.createElement('td');
    var text = document.createElement('input');
    text.setAttribute('type', 'text');
    text.setAttribute('id', textid);
    text.setAttribute('class', 'form-control');
    td2.appendChild(text);

    var td3 = document.createElement('td');
    td3.setAttribute('class', 'td-actions text-right');
    var addTask = document.createElement("button");
    addTask.setAttribute('id', buttonId);
    addTask.setAttribute('title', 'Add Task');
    addTask.setAttribute('class', 'btn btn-white btn-link btn-lg');
    addTask.setAttribute('onclick','addTasktoDatabase()');
    var icon = document.createElement('i');
    icon.setAttribute('class', 'material-icons');
    icon.innerHTML = 'add';
    addTask.appendChild(icon);

    td3.appendChild(addTask);
    addTask.appendChild(icon);

    tr.appendChild(td1);
    tr.appendChild(td2);
    tr.appendChild(td3);
    tbody.appendChild(tr);

    add_task = document.getElementById('add'+i+'-task');
    task_text = document.querySelector('#task'+i+'-text');

}

console.log(add_task);


/************************ Speech to text, transcript and summary part ****************************/  
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

    if(data.command == 'summarize') {
        summary_field.innerHTML = '';
        transcript.innerHTML += data.transcript;
        summary_field.innerHTML += data.summary;
    }
    else if (data.command == 'translate'){
        console.log(data.translated_summary)
        if (data.translated_summary != ''){
            document.querySelector('#summary-text').innerHTML = data.translated_summary;
        }    
    }
    else if (data.command == 'fetch'){
        transcript.innerHTML = data.transcript;
        console.log(transcript.textContent);
        summary_field.innerHTML = data.summary;
        document.querySelector('#summary-text').innerHTML = data.translated_summary;
    }
    chatSocket.send(JSON.stringify({
        'command': 'save_meeting_info',
        'final_transcript':transcript.textContent,
        'final_summary':summary_field.textContent,
        'final_translated_summary':document.querySelector('#summary-text').textContent
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
