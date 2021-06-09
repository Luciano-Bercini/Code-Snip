hljs.highlightAll();
trackRatingValue();

let ratingValue = 0;

function trackRatingValue() {
    $(".rating input:radio").click(() => {
        ratingValue = $(":checked").val();
    })
}
function review() {
     $.ajax({
        type: 'POST',
        url: window.location.href + '/rate_snippet',
        data: {
            rating: ratingValue,
            review: $("#review").val()
    },
    success: (result) => {
           alert(result);
    },
    error: function(request) {
           alert(request.responseJSON);
        }
    });
}
function copyToClipboard() {
    let textToCopy = $("code").text();
    if (navigator.clipboard) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert("Successfully copied the code to the clipboard!");
        }).catch(() => {
            alert("Error copying the code to the clipboard!");
        })
    }
}