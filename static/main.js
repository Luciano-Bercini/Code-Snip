//insertHeader();
registerServiceWorker();

function registerServiceWorker() {
    window.addEventListener('load', () => {
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker.register("static/serviceworker.js").then(function (registration) {
                // Service worker registered correctly.
                console.log("ServiceWorker registration successful with scope: ", registration.scope);
            }, error => {
                console.log('ServiceWorker registration failed: ', error);
            })
        }
    })
}
function renderQueryTableInElement(jQueryTableIndex) {
    $.ajax({
    type: 'GET',
    url: '/render_query_table',
    data: {
        title: $("#title").val(),
        language: $("#language").val()
    },
    success: (data) => {
        $(jQueryTableIndex).empty().append(data);
    },
    error: function(error) {
        console.log("Here is the error res: " + JSON.stringify(error));
    }
})
}
function insertHeader()
{
    let header = document.createElement("header");
    let nav = document.createElement("nav");
    nav.className = "pure-g";

    const internalDivClassName = "pure-u-1-3 centered-text big-text"

    let homeLink = document.createElement("div");
    homeLink.innerHTML = "<a href='templates/index.html'><p>Home</p></a>";
    homeLink.className = internalDivClassName;

    let informationLink = document.createElement("div");
    informationLink.innerHTML = "<a href='templates/information.html'><p>Information</p></a>";
    informationLink.className = internalDivClassName;

    let contactLink = document.createElement("div");
    contactLink.innerHTML = "<a href=templates/contact.html><p>Contact</p></a>";
    contactLink.className = internalDivClassName;


    nav.appendChild(homeLink);
    nav.appendChild(informationLink);
    nav.appendChild(contactLink);

    header.appendChild(nav);

    document.body.insertBefore(header, document.body.firstChild);
}
/*function updateCode(text) {
  let result_element = document.querySelector("#highlight-content");
  result_element.innerHTML = text.replace(new RegExp("&", "g"), "&").replace(new RegExp("<", "g"), "<");
  hljs.highlightBlock(result_element);
}*/