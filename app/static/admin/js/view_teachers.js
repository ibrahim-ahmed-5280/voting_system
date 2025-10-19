function teacher_registration(id) {
    const form = document.getElementById('teacher_form' + id);
    const name = document.getElementById('name' + id).value.trim();
    const teacherId = document.getElementById('teacher_id' + id).value.trim();
    const button = document.getElementById('submit_button' + id);
    const spinner = document.getElementById('spinner' + id);
    const buttonText = button.querySelector('.button-text');

    const nameError = document.getElementById('name_error' + id);
    const idError = document.getElementById('teacher_id_error' + id);
    const succ_msg = document.getElementById('succ_msg' + id);
    const err_msg = document.getElementById('err_msg' + id);

    // --- Reset previous errors ---
    [nameError, idError, succ_msg, err_msg].forEach(err => {
        err.innerHTML = "";
        err.classList.add('d-none');
    });

    let hasError = false;

    // --- Validate Full Name ---
    const nameParts = name.split(' ').filter(Boolean);
    if (nameParts.length < 3 || nameParts.length > 4) {
        nameError.classList.remove('d-none');
        nameError.innerHTML = "Full name must contain 3–4 parts.";
        hasError = true;
    } else if (!nameParts.every(part => /^[A-Za-z]{3,15}$/.test(part))) {
        nameError.classList.remove('d-none');
        nameError.innerHTML = "Each name part must be 3–15 alphabetic characters.";
        hasError = true;
    }

    // --- Validate teacher ID ---
    if (!/^(?!0$)[0-9]{1,10}$/.test(teacherId)) {
        idError.classList.remove('d-none');
        idError.innerHTML = "teacher ID must be numeric (1–10 digits).";
        hasError = true;
    }

    if (hasError) return;

    // --- Disable button during submission ---
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Submitting...';

    // --- Send data to backend ---
    fetch('/update_teacher_details', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, name, teacher_id: teacherId })
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                succ_msg.classList.remove('d-none');
                succ_msg.innerHTML = data.message;
                console.log(data, succ_msg);
                // form.reset(); // Uncomment if you want to clear the form after success
            } else {
                console.log(data);
                err_msg.classList.remove('d-none');
                err_msg.innerHTML = data.message;
            }
        })
        .catch(err => {
            console.error('Error:', err);
            err_msg.classList.remove('d-none');
            err_msg.innerHTML = "Something went wrong. Try again.";
        })
        .finally(() => {
            // --- Reset button state ---
            button.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Submit';
        });
}

function togglePassword(fieldId, id) {
    const input = document.getElementById(fieldId + id);
    const icon = document.getElementById('icon_eye' + id);

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    }
}

function change_password_teacher(id) {
    const form = document.getElementById('teacher_form' + id);
    const password = document.getElementById('password' + id).value.trim();
    const confirm_password = document.getElementById('confirm_password' + id).value.trim();
    const button = document.getElementById('submit_button_pass' + id);
    const spinner = document.getElementById('spinner_pass' + id);
    const buttonText = button.querySelector('.button-text');

    const passError = document.getElementById('passError' + id);
    const ConfirmError = document.getElementById('ConfirmError' + id);
    const succ_msg = document.getElementById('succ_msg_pass' + id);
    const err_msg = document.getElementById('err_msg_pass' + id);

    // --- Reset previous errors ---
    [passError, ConfirmError, succ_msg, err_msg].forEach(err => {
        err.innerHTML = "";
        err.classList.add('d-none');
    });

    let hasError = false;

    // --- Validate password ---
    if (password.length < 6 || password.length > 20) {
        passError.classList.remove('d-none');
        passError.innerHTML = "password must be 6-20 chars.";
        hasError = true;
    }
    // --- Validate confirm password ---
    if (!confirm_password || confirm_password != password) {
        ConfirmError.classList.remove('d-none');
        ConfirmError.innerHTML = "Confirm password not match the password.";
        hasError = true;
    }

    if (hasError) return;

    // --- Disable button during submission ---
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Updating...';

    // --- Send data to backend ---
    fetch('/change_password_teacher', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_password: password, confirm_password, id })
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                succ_msg.classList.remove('d-none');
                succ_msg.innerHTML = data.message;
                console.log(data, succ_msg);
                // form.reset(); // Uncomment if you want to clear the form after success
            } else {
                console.log(data);
                err_msg.classList.remove('d-none');
                err_msg.innerHTML = data.message;
            }
        })
        .catch(err => {
            console.error('Error:', err);
            err_msg.classList.remove('d-none');
            err_msg.innerHTML = "Something went wrong. Try again.";
        })
        .finally(() => {
            // --- Reset button state ---
            button.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Submit';
        });
}
