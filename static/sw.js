let cacheName = "Code Snip";

let filesToCache = [
    "static/jquery-3.6.0.min.js",
    "static/post_snippet.js",
    "static/manifest.json",
    "static/search_snippets.js",
    "static/styles.css",
    "static/update_snippet.js",
    "static/user_snippets.js",
    "static/view.js"
];

// Start the service worker and cache all of the static app's content.
self.addEventListener("install", event => {
    event.waitUntil(caches.open(cacheName).then(cache => {
        return cache.addAll(filesToCache);
    }));
});

// If a request doesn't match anything in the cache, get it from the network, send it to the page and add it to the cache at the same time.
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.open(cacheName).then(cache => {
            return cache.match(event.request).then(response => {
                return response || fetch(event.request).then(response => {
                    cache.put(event.request, response.clone());
                    return response;
                })
            })
        })
    )
})

/*
// Using a "cache then network" approach to serve the content (loads network content as soon as available).
self.addEventListener("fetch", event => {
    event.respondWith(caches.match(event.request).then(response => {
        if (response) {
            return response;
        }
        return fetch(event.request);
        fetch(event.request).then(response => {
            if (!response.ok) {
                throw new TypeError("Bad response status!");
            }
            caches.open(cacheName).then(cache => {
                return cache.put(event.request, response);
            })
        })
    }));
});
*/