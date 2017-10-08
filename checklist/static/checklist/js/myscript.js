var warnColor = '#dd5555';
var popupColor = '#6666dd';
var i = 0;
function popup(text) {
    _popup(text, popupColor);
};

function popup_warn(text) {
    _popup(text, warnColor);
};

function _popup(text, color) {
    if (text == '') {
        text = 'Default popup string';
    }
    var pop = document.getElementById('popup_notif');
    if (!pop) {
        pop = document.createElement("div");
        pop.className = "popupDiv";
        pop.id='popup_notif';
        pop.style.backgroundColor = color;
        document.body.appendChild(pop);

        var close = document.createElement("a");
        close.id = "close_btn";
        close.className="dismissBtn";
        var closeImg = document.createElement("img");
        closeImg.src = "img/closebtn.png";
        closeImg.style.heigh = "1.25em";
        closeImg.style.width = "1.25em";
        close.appendChild(closeImg);
        close.onclick = remove_popup;
        pop.appendChild(close);

        var popLabel = document.createElement("label");
        popLabel.id = "pop_label";
        popLabel.textContent = text;
        pop.appendChild(popLabel);
    } else {
        pop.style.backgroundColor = color;
        var popLabel = document.getElementById("pop_label");
        popLabel.textContent = text;
    }

    document.getElementById('btnClear').disabled = false;
}

function remove_popup() {
    document.getElementById('btnClear').disabled = true;
    var pop = document.getElementById('popup_notif');
    $(pop).fadeOut('', function(){
        pop.parentNode.removeChild(pop);
    });
};