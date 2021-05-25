let cacheName = "Code Snip";

let filesToCache = [
    "index.html",
    "contact.html",
    "information.html",
    "styles.css",
    "main.js"
];

// Start the service worker and cache all of the app's content.
self.addEventListener("install", event => {
    event.waitUntil(caches.open(cacheName).then(cache => {
        return cache.addAll(filesToCache);
    }));
});

// Using a "cache then network" approach to serve the content (loads network content as soon as available).
self.addEventListener("fetch", event => {
    event.respondWith(caches.match(event.request).then(response => {
        if (response) {
            return response;
        }
        return fetch(event.request);
    }));
});