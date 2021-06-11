let table = $('#table');

$(document).ready(function () {
    renderUserTable('#table');
    $('#search').submit(function (e) {
        e.preventDefault();
        renderUserTable();
    });
});

function renderUserTable() {
    $.ajax({
        type: 'GET',
        url: '/render_user_snippets_table',
        success: (data) => {
            table.html(data);
        },
        error: function(error) {
            alert(error);
        }
    })
}
function deleteSnippet(id) {
        $.ajax({
        type: 'POST',
        url: '/delete_snippet/' + id,
        success: (data) => {
            renderUserTable();
        },
        error: function(error) {
            alert(error);
        }
    })
}
