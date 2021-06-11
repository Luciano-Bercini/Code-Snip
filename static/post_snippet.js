let showTime = 500;
let fadeOutTime = 4000;

$(document).ready(function () {
    // Making sure the elements are not visible even while loading the page using a temporary class hidden.
    $('#success').removeClass('hidden').hide();
    $('#failure').removeClass('hidden').hide();
    $('#post').submit(function (e) {
        e.preventDefault();
        $.ajax({
        type: 'POST',
        url: '/post_snippet',
        data: {
        title: $("#title").val(),
        content: $("#content").val(),
        language: $("#language").val()
    },
    success: (result) => {
        $('#success').hide();
        $('#failure').hide();
        let title = $("#title").val();
        if (result === "success") {
            let successString = `Successfully submitted ${ title } `;
            $('#success').html(successString).show(showTime).fadeOut(fadeOutTime);
        }
        else {
            let failString = `Failed to submit: ${ result }`;
            $('#failure').text(failString).show(showTime).fadeOut(fadeOutTime);
        }
    },
    error: function(error) {
        console.log("Error: " + JSON.stringify(error));
        }
    })
    });
});