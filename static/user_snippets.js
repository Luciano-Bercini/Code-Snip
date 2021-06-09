$(document).ready(function () {
    renderQueryTableInElement('#table');
    $('#search').submit(function (e) {
        e.preventDefault();
        renderQueryTableInElement('#table');
    });
});

function renderQueryTableInElement(jQueryTableIndex) {
    $.ajax({
        type: 'GET',
        url: '/render_user_snippets_table',
        success: (data) => {
            $(jQueryTableIndex).empty().append(data);
        },
        error: function(error) {
            console.log("Error: " + JSON.stringify(error));
        }
    })
}
