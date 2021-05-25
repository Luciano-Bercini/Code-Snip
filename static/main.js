registerServiceWorker()

function registerServiceWorker() {
    window.addEventListener('load', () => {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').then(function (registration) {
                // Service worker registered correctly.
                console.log("ServiceWorker registration successful with scope: ", registration.scope);
            }, error => {
            console.log('ServiceWorker registration failed: ', error);
            })
        }
    })
}
