let popupOpen = false;

const popups = document.getElementById('popups');

function togglePopup() {
    popups.style.display = popupOpen ? 'none' : '';

    rootElement.style.overflow = popupOpen ? '' : 'hidden';

    popupOpen = !popupOpen;
}

function sendReachOutTicket(event) {

}