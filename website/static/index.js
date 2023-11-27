function leaguemain(leagueid, button) {
    // Traverse up the DOM to find the closest form element
    var form = button.closest(".edit-league-form");

    // Check if a form was found
    if (form) {
        var input = form.querySelector("input[name='leagueid']");
        input.value = leagueid;
        form.submit();
    } else {
        console.error("Form not found");
    }
}