/* Events for delete account */

// Queries of the page
const username = document.querySelector('#username');
const password = document.querySelector('#password');
const accept = document.querySelector('#accept');

// Calls to the function through an event
username.onkeyup = onKeyUp;
password.onkeyup = onKeyUp;

// Disable the shadow style effect
accept.style.boxShadow = 'none';

// Function for disabling the button
function onKeyUp() {
    if (username.value === '' || password.value === '') {
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