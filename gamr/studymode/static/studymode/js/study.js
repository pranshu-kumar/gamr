
var pastedText = document.querySelector('#pasted-text');
var summaryText = document.querySelector('#summary-text');
var lentext = document.querySelector('#lentext');
var lensummary = document.querySelector('#lensummary');
var list = document.querySelector('#list');
var parabox = document.querySelector('#para');
var namedent = document.querySelector("#namedent");
var blur = document.getElementById('blur');
var loading = document.getElementById('loading');

{/* <li>
        <div class="resources1">
            <div class="resourceheader"><span>Abstractive Summarization of Dialogues </span></div>
            <div class="resourcesite"> <a href="#">https://towardsdatascience.com/abstractive-summarization-of-dialogues-f530c7d290be</a></div>
            <div class="resourcedescription"><span>" There are 2.5 quintillion bytes of data created each day" - That was 2017 and now we seem to have lost the count. Putting things ...
            </span></div>
            <div class="resourceimage"><img src="{% static 'studymode/media/unfurling.jpg' %}" width="350px" height="200px"></div>
            <div class="box"></div>
            <div class="resourcetag">
                <span>We feel that this resource would be of great help for you in understanding the concept. This resource has been chosen based on its popularity and reviews.</span>
            </div>
        </div>
    </li> */}

function addResources(){

    
    blur.style.filter = "blur(2px)";
    var childNodes = blur.getElementsByTagName('*');
    for (var node of childNodes) {
        node.disabled = true;
    }
    loading.style.visibility = "visible";
    studySocket.send(JSON.stringify({
        'command': 'add_resources',
        'pasted_text': pastedText.value
    }));
}

function showResources(data, i){

    blur.style.filter = "";
    var childNodes = blur.getElementsByTagName('*');
    for (var node of childNodes) {
        node.disabled = false;
    }
    loading.style.visibility = "hidden";
    
    var li = document.createElement('li');
    var div1 = document.createElement('div');
    div1.setAttribute('class', 'resources'+i);
    li.appendChild(div1);

    var div2 = document.createElement('div');
    div2.setAttribute('class', 'resourceheader');
    var span1 = document.createElement('span');
    if("title" in data) {
        span1.innerHTML = data.title;
    } else {
        span1.innerHTML = "Website"
    }
    div2.appendChild(span1);

    var div3 = document.createElement('div');
    div3.setAttribute('class', 'resourcesite');
    var a = document.createElement('a');
    a.setAttribute('href', data.url);
    a.setAttribute('target', '_blank')
    a.innerHTML = data.url;
    div3.appendChild(a);

    var div4 = document.createElement('div');
    div4.setAttribute('class', 'resourcedescription');
    var span2 = document.createElement('span');
    if("description" in data) {
        span2.innerHTML = data.description;
    } else {
        span2.innerHTML = "No Description.";
    }
    div4.appendChild(span2);

    var div5 = document.createElement('div');
    div5.setAttribute('class', 'resourceimage');
    var img = document.createElement('img');
    img.setAttribute('width', '350px');
    img.setAttribute('height', '200px');
    if("image" in data){
        img.setAttribute('src', data.image);

        img.onerror = function(e) {
            img.src = "/static/studymode/media/unfurling.jpg"
        };
    } else {
        img.setAttribute('src', '/static/studymode/media/unfurling.jpg');
    }
    div5.appendChild(img);

    var div6 = document.createElement('div');
    div6.setAttribute('class', 'box');

    var div7 = document.createElement('div');
    div7.setAttribute('class', 'resourcetag');
    var span3 = document.createElement('span');
    if("type" in data) {
        span3.innerHTML = "<b>Type: </b>" + data.type;
    } else {
        span3.innerHTML = "<b>Type:</b> website";
    }
    div7.appendChild(span3);

    div1.appendChild(div2);
    div1.appendChild(div3);
    div1.appendChild(div4);
    div1.appendChild(div5);
    div1.appendChild(div6);
    div1.appendChild(div7);

    list.appendChild(li);

}

function changeTextToPara(words, tokens){

    var p = document.createElement('p');
    var keywords_text = change_text(pastedText.value, words, tokens);
    p.innerHTML = keywords_text;
    parabox.appendChild(p);
    pastedText.parentElement.removeChild(pastedText);
}

function change_text(text, words, tokens){
    for(var i = 0; i < words.length; i = i+1){
        var re = new RegExp(words[i], "");
        text = text.replace(re, "<a class=\""+tokens[words[i]]+"\">"+words[i]+"</a>");
    }
    return text;
}

{/* <div class="word">
		<a href="#" class="hover"><span>Keyword</span> 
			<div class="hoverbox"> 
				<div class="mainbox"> 
					<a href="#"> 
						<span class="entity"><B>ENTITY</B></span> 
						<div class="line"></div> 
						<a class="keyword">Keyword</a> 
						<span class="description">Habitasse senectus varius nisi ultrices, torquent urna. Conubia pellentesque consequat taciti eleifend felis vestibulum duis gravida quam elit vivamus. Dui sociis penatibus aliquet est eleifend? Ullamcorper aenean sagittis consequat, sem nascetur litora. Conubia, cursus hendrerit placerat! Aliquam curabitur sapien luctus nisi. Proin lorem laoreet tortor ipsum nisl morbi sed. Neque risus fermentum tortor quis lacus posuere cubilia enim imperdiet facilisis elit? Parturient; volutpat mattis odio nostra amet montes tellus donec. Ut ultrices porta orci sit nulla lectus sociosqu. Venenatis varius turpis morbi justo lectus habitasse ultricies dui integer conubia at. Maecenas faucibus, primis vitae. Platea, platea etiam massa libero rutrum?</span>
						<div class="line2"></div>
						<a href="#" class="link" style="color:#7b5fe5">www.linkofthewebsite.com</a>
						<div class="cross1"></div>
						<div class="cross2"></div>
					</a>
				</div>
			</div>
		</a>
	</div> */}

// crossbutton on dialouge

function summarize(val) {
    studySocket.send(JSON.stringify({
        'command': 'process_pasted_text',
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
    if(data.command == 'show_summary'){
        summaryText.innerHTML = data.summary;
        lensummary.innerHTML = data.len_summary;
        lentext.innerHTML = data.len_text;
    } 
    else if(data.command == 'show_resources'){
        var tokens = data.tokens;
        var resources_data = data.all_resources;
        var l = Object.keys(tokens);
        namedent.innerHTML = l.length;
        changeTextToPara(Object.keys(tokens), tokens);
        if(list.childElementCount){
            var p = list.parentElement;
            list.parentElement.removeChild(list);
            list = document.createElement('ul');
            list.id = "list";
            p.appendChild(list);
        }
        for(var i = 0; i < resources_data.length; i=i+1) {
            var resource_dir = resources_data[i];
            showResources(resource_dir, i+1);
        } 
    }
    
}
