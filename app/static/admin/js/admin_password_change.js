function togglePasswordVisibility(fieldId, button) {
    const input = document.getElementById(fieldId);
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    }
}

function setInvalid(fieldId, message) {
    const input = document.getElementById(fieldId);
    const feedback = document.getElementById(fieldId + 'Feedback');

    if (!input || !feedback) return;

    input.classList.add('is-invalid');
    feedback.style.display = 'block'; 
    feedback.textContent = message; // Or innerText
}

function submit_password_admin() {
    const errorElement = document.getElementById('passwordError');
    const successElement = document.getElementById('passwordSuccess');
    const form = document.getElementById('changePasswordForm');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btnText');

    // Reset alerts and feedback
    errorElement.classList.add('d-none');
    successElement.classList.add('d-none');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');

    // Gather values
    const admin_id = document.getElementById('admin_id').value.trim();
    const oldPassword = document.getElementById('oldPassword').value.trim();
    const newPassword = document.getElementById('newPassword').value.trim();
    const confirmPassword = document.getElementById('confirmPassword').value.trim();

    // Validation
    let isValid = true;

    if (!oldPassword) {
        setInvalid('oldPassword', 'Current password is required.');
        isValid = false;
    }

    if (!newPassword) {
        setInvalid('newPassword', 'New password is required.');
        isValid = false;
    } else if (newPassword.length < 6 || newPassword.length > 20) {
        setInvalid('newPassword', 'Password must be at least 6 to 20 characters long.');
        isValid = false;
    }

    if (!confirmPassword) {
        setInvalid('confirmPassword', 'Please confirm your new password.');
        isValid = false;
    } else if (newPassword !== confirmPassword) {
        setInvalid('confirmPassword', 'Passwords do not match.');
        isValid = false;
    }

    if (!isValid) {
        return;
    }

    // Show spinner and disable button
    spinner.classList.remove('d-none');
    btnText.textContent = 'Processing...';
    document.getElementById('changePasswordBtn').disabled = true;

    // Prepare data
    const data = {
        admin_id,
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
    };
    console.log('data submitted ',data)
    // Send request
    fetch('/change_password_admin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Hide spinner and re-enable button
        spinner.classList.add('d-none');
        btnText.textContent = 'Change Password';
        document.getElementById('changePasswordBtn').disabled = false;

        if (data.success) {
            successElement.textContent = data.message || 'Password changed successfully!';
            successElement.classList.remove('d-none');
            form.reset();

            // Close the modal
            setTimeout(() => {
                const modalEl = document.getElementById('changePasswordModal');
                if (modalEl) {
                    const modalInstance = bootstrap.Modal.getInstance(modalEl);
                    if (modalInstance) modalInstance.hide();
                    successElement.classList.add('d-none');
                }
            }, 2000);
        } else {
            errorElement.textContent = data.message || 'An error occurred.';
            errorElement.classList.remove('d-none');
            if (data.errors) {
                if (data.errors.old_password) setInvalid('oldPassword', data.errors.old_password);
                if (data.errors.new_password) setInvalid('newPassword', data.errors.new_password);
                if (data.errors.confirm_password) setInvalid('confirmPassword', data.errors.confirm_password);
            }
        }
    })
    .catch(err => {
        // Hide spinner and re-enable button
        spinner.classList.add('d-none');
        btnText.textContent = 'Change Password';
        document.getElementById('changePasswordBtn').disabled = false;

        console.error('Error:', err);
        errorElement.textContent = 'Network error occurred. Please try again.';
        errorElement.classList.remove('d-none');
    });
}

function toggleFormVisibility() {
    const form = document.getElementById('formChange');
    form.classList.toggle('d-none');
}

function submit_changes() {
    const button = document.querySelector('#formChange .btn-with-spinner');
    const spinner = button.querySelector('.spinner-border');
    const buttonText = button.querySelector('.button-text');
    const succ_msg = document.getElementById("alert_success");
    const error_msg = document.getElementById("alert_error");

    spinner.classList.remove('d-none');
    buttonText.textContent = 'Processing...';
    button.disabled = true;

    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';
    // Validate all fields
    let isValid = true;

    // Name validation
    const name = sanitizeInput(document.getElementById('name').value);
    if (!name) {
        showError('name', 'Name is required');
        isValid = false;
    } else {
        hideError('name');
    }

    // Email validation
    const email = sanitizeInput(document.getElementById('type_email').value);
    if (!email) {
        showError('email', 'Email is required');
        isValid = false;
    } else if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email address');
        isValid = false;
    } else {
        hideError('email');
    }


    

    if (!isValid) {
        spinner.classList.add('d-none');
        buttonText.textContent = 'Submit';
        button.disabled = false;
        return;
    }

    // Prepare form data
    const formData = {
        admin_id: document.getElementById("admin_id").value,
        name: name,
        email: email
    };
    console.log(formData)
    // Send to backend
    fetch('/change_admin_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status) {
            error_msg.style.display = 'none';
            succ_msg.style.display = 'block';
            succ_msg.innerHTML = data.message || 'success to update user details';
            // Optional: Refresh user data
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            succ_msg.style.display = 'none';
            error_msg.style.display = 'block';
            error_msg.innerHTML = data.message || 'Failed to update user details';
            // Show field-specific errors if available
            if (data.errors) {
                Object.entries(data.errors).forEach(([field, message]) => {
                    showError(field, message);
                });
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        succ_msg.style.display = 'none';
        error_msg.style.display = 'block';
        error_msg.innerHTML = 'Network error occurred. Please try again.';
    })
    .finally(() => {
        spinner.classList.add('d-none');
        buttonText.textContent = 'Submit';
        button.disabled = false;
    });
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    return input.trim()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#x27;");
}

function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}Error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

function hideError(fieldId) {
    const errorElement = document.getElementById(`${fieldId}Error`);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}
