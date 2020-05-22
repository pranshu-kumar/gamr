
var pastedText = document.querySelector('#pasted-text');
var summaryText = document.querySelector('#summary-text');
var lentext = document.querySelector('#lentext');
var lensummary = document.querySelector('#lensummary');


function summarize(val) {
    
    studySocket.send(JSON.stringify({
        'commands': 'process_pasted_text',
        'pasted_text': val
    }));
    
}

const username = JSON.parse(document.getElementById('username').textContent);

const studySocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/study/'
    + username
    + '/dashboard/'
);

studySocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

studySocket.onopen = function (e) {
    console.log('connected');
}

studySocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    summaryText.innerHTML = data.summary;
    lensummary.innerHTML = data.len_summary;
    lentext.innerHTML = data.len_text;
}