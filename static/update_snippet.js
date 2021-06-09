let showTime = 500;
let fadeOutTime = 4000;

$(document).ready(function () {
    // Making sure the elements are not visible even while loading the page using a temporary class hidden.
    let successText = $('#success')
    let failureText = $('#failure')
    successText.removeClass('hidden').hide();
    failureText.removeClass('hidden').hide();
    $('#post').submit(function (e) {
        e.preventDefault();
        $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
        title: $("#title").val(),
        content: $("#content").val(),
        language: $("#language").val()
    },
    success: (result) => {
        successText.hide();
        failureText.hide();
        let title = $("#title").val();
        if (result === "success") {
            let successString = `Successfully updated ${ title } `;
            successText.text(successString).show(showTime).fadeOut(fadeOutTime);
        }
        else {
            let failString = `Failed to submit: ${ result }`;
            failureText.text(failString).show(showTime).fadeOut(fadeOutTime);
        }
    },
    error: function(error) {
        console.log("Error: " + JSON.stringify(error));
        }
    })
    });
});