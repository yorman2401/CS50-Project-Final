/* Events for modal */

// Queries of the page
const modaluser = document.querySelector('#modaluser');
const modalpass = document.querySelector('#modalpass');
const modalacce = document.querySelector('#modalacce');

// Calls to the function through an event
modaluser.onkeyup = onKeyUp;
modalpass.onkeyup = onKeyUp;

// Disable the shadow style effect
modalacce.style.boxShadow = 'none';

// Function for disabling the button
function onKeyUp() {
    if (modaluser.value === '' || modalpass.value === '') {
        modalacce.disabled = true;

        // Disable the shadow style effect
        modalacce.style.boxShadow = 'none';
    }
    else {
        modalacce.disabled = false;

        // Enable the shadow style effect
        modalacce.style.boxShadow = '';
    }
}