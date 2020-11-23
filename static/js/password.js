/* Events for change password */

// Queries of the page
const current = document.querySelector('#current');
const password = document.querySelector('#password');
const confirm = document.querySelector('#confirm');
const accept = document.querySelector('#accept');

// Calls to the function through an event
current.onkeyup = onKeyUp;
password.onkeyup = onKeyUp;
confirm.onkeyup = onKeyUp;

// Disable the shadow style effect
accept.style.boxShadow = 'none';

// Function for disabling the button
function onKeyUp() {
    if (current.value === '' || password.value === '' || confirm.value === '') {
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