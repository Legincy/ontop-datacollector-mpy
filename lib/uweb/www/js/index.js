//let sessionValid = {ssid: false, password: false, gateway: false, subnet: false, "static-ip": true};
let sessionValid = {ssid: false, password: false};
const isStaticIPEnabled = document.getElementById("cb-static-ip");

const inputFields = document.getElementsByTagName('input');
Array.from(inputFields).forEach((child) => child.addEventListener('input', validate))

function getUID() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    const uid = document.getElementById("uid");
    const urlUID = urlParams.get('uid')

    uid.innerHTML = urlUID || "";
}
function changeVisibility(e) {
    document.getElementById("div-static-ip").style.visibility = "visible";
    if (e.checked) {
        document.getElementById("div-static-ip").style.visibility = "hidden";
    }

    validate(e);
}

function validate(e){
    let rgx;
    const newValue = e.target.value

    switch(e.target.id){
        case "gateway":
            rgx = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$/;
            break;
        case "static-ip":
            rgx = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$/;
            break;
        case "subnet":
            rgx = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$/;
            break;
        case "ssid":
            rgx = /^[^!#;+\]\/"\t][^+\]\/"\t]{0,30}[^ +\]\/"\t]$|^[^ !#;+\]\/"\t]$[ \t]+$/;
            break;
        case "password":
            sessionValid.password = newValue.length >= 5;
            break;
        case "cb-static-ip":
            sessionValid["static-ip"] = !!isStaticIPEnabled.checked;
            break;
        default:
            break;
    }

    if(rgx) {
        sessionValid[e.target.id] = !!newValue.match(rgx);
    }

    updateSession();
} 

function updateSession(){
    document.getElementById("save-btn").disabled = Object.keys(sessionValid).some(key => sessionValid[key] === false);
}
