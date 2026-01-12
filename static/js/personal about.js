const windows = {
    'mail' : document.getElementById('emails-window'),
    'search' : document.getElementById('search-engine'),
    'messages' : document.getElementById('messenger-window')
};

const zOrder = {
    'mail' : 10,
    'search' : 9,
    'messages' : 8,
};

function bumpWindow(key) {
    if (zOrder[key] == 10)
        return;

    for (const k in zOrder) {
        if (k == key)
            zOrder[k] = 10;
        else 
            zOrder[k]--;
        windows[k].style.zIndex = zOrder[k];
    }
}

function openWindow(key) {
    windows[key].style.display = 'block';
    bumpWindow(key);
}

function closeWindow(key) {
    windows[key].style.display = 'none';
}

for (const key in windows) {
    closeWindow(key);
}

const desktop = document.getElementById('desktop');

let dragOffset, currWindow, currTitlebar,
    dragging = false;

// draggable windows
desktop.addEventListener('pointerdown', e => {
    currWindow = e.target.closest('.window');
    currTitlebar = e.target.closest('.title-bar');
    
    if (currTitlebar) {
        const rect = currWindow.getBoundingClientRect();

        dragOffset = [e.clientX - rect.left, e.clientY - rect.top];
        dragging = true; 
    } 
    if (!currWindow)
        return;

    bumpWindow(currWindow.dataset.windowKey);
});

desktop.addEventListener('pointerup', e => {
    currWindow = null;
    currTitlebar = null;
    dragging = false;
});

desktop.addEventListener('pointermove', e => {
    if (dragging && currWindow) {
        currWindow.style.left = `${e.clientX - dragOffset[0]}px`;
        currWindow.style.top = `${e.clientY - dragOffset[1]}px`;
    }
});

//  open email
const email = document.getElementById('about-me-email'),
    notif = document.getElementById('notif-icon'),
    desktopNotif = document.getElementById('notification-icon');

let emailOpened = false;

function openEmail() {
    if (emailOpened)
        return;

    email.style.display = 'block';
    notif.style.display = 'none';
    desktopNotif.style.display = 'none';
    emailOpened = true;
}

const patchNotesTab = document.getElementById('patch-notes'),
    blogTab = document.getElementById('blog'),
    patchNotesButton = document.getElementById('patch-notes-button'),
    blogButton = document.getElementById('blog-button');

let currentTab = 'patch-notes';

function openTab(id) {
    if (id == currentTab)
        return

    if (id == 'patch-notes') {
        patchNotesTab.style.display = 'block';
        blogTab.style.display = 'none';
        blogButton.classList.remove('selected-tab');
        patchNotesButton.classList.add('selected-tab');
    }
    else {
        patchNotesTab.style.display = 'none';
        blogTab.style.display = 'block';
        blogButton.classList.add('selected-tab');
        patchNotesButton.classList.remove('selected-tab');
    }
    
    currentTab = id;
}