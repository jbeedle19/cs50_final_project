// JS for displaying password criterial on register page
let passwordInputEl = document.querySelector("#password");
let passCriteriaEl = document.querySelector(".pass-restraint");
let headerEl = document.getElementsByTagName("header");

if (headerEl.length != 0) {
    if (passCriteriaEl != null){
        passCriteriaEl.style.display = "block";
    }
}

function displayCriteria(event) {
    event.preventDefault();
    passCriteriaEl.style.display = "block";
}

if (passwordInputEl != null) {
    passwordInputEl.addEventListener("focus", displayCriteria);
}