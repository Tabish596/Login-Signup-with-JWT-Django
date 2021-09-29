'use strict'

const pass = document.getElementById('password');
const confirmPass = document.getElementById('confirm_pass');
const msgArea = document.getElementById('confirm_pass_msg');

confirmPass.addEventListener('keyup', validatePassword);

function validatePassword(event) {
    let value = event.target.value;
    if (pass.value === value) {
        msgArea.innerText = 'Password Matched';
    } else {
        msgArea.innerText = 'Password not matched!!';
    }
}