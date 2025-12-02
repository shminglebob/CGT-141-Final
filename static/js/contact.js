const subscribeForm = document.getElementById('subscription-form'),
    emailInput = document.getElementById('subscription-email');

function submitSubscribeForm(event) {
    event.preventDefault();

    $.ajax({
        type : 'POST',
        url : '/subscribe',
        data : JSON.stringify({
            email: emailInput.value
        }),
        contentType : 'application/json',
        success: function (response) {
            alert('Successfully subscribed!');
        },
        error: function (response) {
            if (response.status == 409)
                alert('Email already subscribed.');
            else
                alert('An error occurred, please try again later.');
        }
    });
}
