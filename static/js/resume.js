let popupOpen = false;

const popups = document.getElementById('popups');

function togglePopup() {
    popups.style.display = popupOpen ? 'none' : '';

    rootElement.style.overflow = popupOpen ? '' : 'hidden';

    popupOpen = !popupOpen;
}

const nameInput = document.getElementById('name'),
    emailInput = document.getElementById('email'),
    reasonInput = document.getElementById('reason'),
    companyInput = document.getElementById('company'),
    messageInput = document.getElementById('message');

function sendReachOutTicket(event) {
    event.preventDefault();
    
    $.ajax({
        type: 'POST',
        url: '/contact-form',
        data: JSON.stringify({
            name: nameInput.value,
            email: emailInput.value,
            reason: reasonInput.value,
            company: companyInput.value,
            message: messageInput.value
        }),
        'contentType': 'application/json',
        success: function (response) {
            if (response == 'success') {
                alert('email sent successfully!');
                togglePopup();
            }
        },
    });
}