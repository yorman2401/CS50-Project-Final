/* Events for change username */

// Queries of the page
const current = document.querySelector('#current');
const username = document.querySelector('#username');
const password = document.querySelector('#password');
const accept = document.querySelector('#accept');

// Calls to the function through an event
current.onkeyup = onKeyUp;
username.onkeyup = onKeyUp;
password.onkeyup = onKeyUp;

// Disable the shadow style effect
accept.style.boxShadow = 'none';

// Function for disabling the button
function onKeyUp() {
    if (current.value === '' || username.value === '' || password.value === '') {
        accept.disabled = true;

        // Disable the shadow style effect
        accept.style.boxShadow = 'none';
    }
    else {
        accept.disabled = false;

        // Enable the shadow style effect
        accept.style.boxShadow = '';
    }
}