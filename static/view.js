hljs.highlightAll();
bindClickToRate();

function bindClickToRate() {
    $(".rating input:radio").click(() => {
        let radioValue = $(":checked").val();
        rate(radioValue);
    })
}
function rate(value) {
     $.ajax({
        type: 'POST',
        url: window.location.href + '/rate_snippet',
        data: {
            rating: value
    },
    success: (result) => {
        console.log(result);
            /*
        if (result === "success") {
            alert("Thanks for reviewing " + value + " stars!");
        }
        else if (result === )
        else {
            alert("Error reviewing the snippet!");
        }*/
    },
    error: function(error) {
        console.log("Here is the error res: " + JSON.stringify(error));
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