function login() {
    const form = document.getElementById('signin_form');
    // Check if form exists
    if (!form) {
        console.error('Form not found');
        return;
    }
    
    const inputs = form.querySelectorAll('input, button');
    const idInput = document.getElementById('studentOrTeacherId')?.value.trim();
    const password = document.getElementById('password')?.value.trim();

    const idError = document.getElementById('studentOrTeacherId_error');
    const passError = document.getElementById('pass_error');
    const button = form.querySelector('button');
    const spinner = document.getElementById('spinner');

    // Check if required elements exist
    if (!button) {
        console.error('Button not found');
        return;
    }

    // Reset error messages
    [idError, passError].forEach(err => {
        if (err) {
            err.style.opacity = 0;
            err.innerHTML = "";
        }
    });

    let hasError = false;

    // --- ID VALIDATION ---
    if (!idInput || idInput.length < 3) {
        if (idError) {
            idError.style.opacity = 1;
            idError.innerHTML = "Please enter a valid Student ID.";
        }
        hasError = true;
    }

    // --- PASSWORD VALIDATION ---
    if (!password || password.length < 4) {
        if (passError) {
            passError.style.opacity = 1;
            passError.innerHTML = "Password must be at least 4 characters.";
        }
        hasError = true;
    }

    if (hasError) return;

    // --- Disable inputs during submission ---
    button.disabled = true;
    
    // Safely handle spinner
    if (spinner) {
        spinner.classList.remove('d-none');
    }
    
    button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...`;

    if (form) form.style.opacity = 0.8;
    inputs.forEach(input => input.disabled = true);

    // --- Send data to backend ---
    fetch('/student_or_teacher_login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: idInput, password })
    })
    .then(res => res.json())
    .then(data => {
        if (form) form.style.opacity = 1;
        inputs.forEach(input => input.disabled = false);

        if (data.success) {
            // Redirect to student dashboard
            window.location.href = data.redirect || '/dashboard_user';
        } else {
            if (data.error === 'invalid_id' && idError) {
                idError.style.opacity = 1;
                idError.innerHTML = data.message || "Invalid Student ID.";
            } else if (data.error === 'invalid_pass' && passError) {
                passError.style.opacity = 1;
                passError.innerHTML = data.message || "Invalid password.";
            } else {
                alert(data.message || "Login failed. Please try again.");
            }
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Something went wrong. Please try again.');
    })
    .finally(() => {
        // Reset button
        if (spinner) {
            spinner.classList.add('d-none');
        }
        button.disabled = false;
        button.innerHTML = `Log In`;

        if (form) form.style.opacity = 1;
        inputs.forEach(input => input.disabled = false);
    });
}