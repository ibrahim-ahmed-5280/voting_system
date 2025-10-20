// password_change.js

// Toggle password visibility
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    }
}

// Validate password field
function validatePassword(id, errorId) {
    const value = document.getElementById(id).value.trim();
    const errorDiv = document.getElementById(errorId);
    let isValid = true;

    if (!value) {
        errorDiv.textContent = 'Password is required';
        isValid = false;
    } else if (value.length < 4) {
        errorDiv.textContent = 'Password must be at least 4 characters';
        isValid = false;
    } else {
        errorDiv.textContent = '';
    }

    errorDiv.style.display = isValid ? 'none' : 'block';
    return isValid;
}

// Validate password confirmation
function validatePasswordConfirmation() {
    const newPassword = document.getElementById('newPassword').value.trim();
    const confirmPassword = document.getElementById('confirmPassword').value.trim();
    const errorDiv = document.getElementById('confirmPasswordError');
    let isValid = true;

    if (!confirmPassword) {
        errorDiv.textContent = 'Please confirm your password';
        isValid = false;
    } else if (newPassword !== confirmPassword) {
        errorDiv.textContent = 'Passwords do not match';
        isValid = false;
    } else {
        errorDiv.textContent = '';
    }

    errorDiv.style.display = isValid ? 'none' : 'block';
    return isValid;
}

// Reset all error messages
function resetErrorMessages() {
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
        el.textContent = '';
    });
    document.getElementById('passwordError').classList.add('d-none');
    document.getElementById('passwordSuccess').classList.add('d-none');
}

// Main submission function
function submit_password_user() {
    resetErrorMessages();

    // Validate all fields
    const isOldPasswordValid = validatePassword('oldPassword', 'oldPasswordError');
    const isNewPasswordValid = validatePassword('newPassword', 'newPasswordError');
    const isConfirmPasswordValid = validatePasswordConfirmation();

    if (!(isOldPasswordValid && isNewPasswordValid && isConfirmPasswordValid)) {
        return;
    }

    // Prepare data
    const formData = {
        old_password: document.getElementById('oldPassword').value.trim(),
        new_password: document.getElementById('newPassword').value.trim(),
        confirm_password: document.getElementById('confirmPassword').value.trim()
    };

    // Show loading state
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btnText');
    const submitBtn = document.getElementById('changePasswordBtn');

    spinner.classList.remove('d-none');
    btnText.textContent = 'Processing...';
    submitBtn.disabled = true;

    // Send request
    fetch('/password_change', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(async (response) => {
            const data = await response.json();

            if (!response.ok) {
                // Handle backend validation errors
                if (data.errors) {
                    for (const [field, message] of Object.entries(data.errors)) {
                        const errorElement = document.getElementById(`${field}Error`);
                        if (errorElement) {
                            errorElement.textContent = message;
                            errorElement.style.display = 'block';
                        }
                    }
                }
                throw new Error(data.message || 'Password change failed');
            }
            return data;
        })
        .then(data => {
            if (data.success) {
                // Show success message
                const successDiv = document.getElementById('passwordSuccess');
                successDiv.textContent = data.message || 'Password changed successfully!';
                successDiv.classList.remove('d-none');

                // Reset form
                document.getElementById('changePasswordForm').reset();

                // Hide modal after delay
                setTimeout(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                    modal.hide();
                    successDiv.classList.add('d-none');
                }, 2000);
            } else {
                throw new Error(data.message || 'Password change failed');
            }
        })
        .catch(error => {
            // Show error message
            const errorDiv = document.getElementById('passwordError');
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('d-none');

            // Scroll to error message
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        })
        .finally(() => {
            // Reset button state
            spinner.classList.add('d-none');
            btnText.textContent = 'Change Password';
            submitBtn.disabled = false;
        });
}