function signup_registration() {
    const form = document.getElementById('signup_form');
    const inputs = form.querySelectorAll('input, button');
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmPassword = document.getElementById('confirm_password').value.trim();

    const nameError = document.getElementById('name_error');
    const emailError = document.getElementById('email_error');
    const passwordError = document.getElementById('password_error');
    const confirmPasswordError = document.getElementById('confirm_password_error');
    const Error = document.getElementById('error');
    const button = document.getElementById('submit_button');
    const spinner = document.getElementById('spinner');
    const buttonText = button.querySelector('.button-text');

    // Reset errors
    [nameError, emailError, passwordError, confirmPasswordError, Error].forEach(err => {
        err.style.opacity = 0;
        err.innerHTML = "";
    });

    let hasError = false;

    // --- NAME VALIDATION ---
    const nameParts = name.split(' ').filter(Boolean); // remove extra spaces

    if (nameParts.length < 3 || nameParts.length > 4) {
        nameError.style.opacity = 1;
        nameError.innerHTML = "Full name must contain 3 or 4 parts (e.g., first, middle, last).";
        hasError = true;
    } else if (!nameParts.every(part => /^[A-Za-z]{3,15}$/.test(part))) {
        nameError.style.opacity = 1;
        nameError.innerHTML = "Each name part must be 3–15 alphabetic characters.";
        hasError = true;
    } else if (name.length < 9 || name.length > 60) {
        nameError.style.opacity = 1;
        nameError.innerHTML = "Full name must be 9–60 characters long.";
        hasError = true;
    }

    // --- EMAIL VALIDATION ---
    const emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!emailPattern.test(email)) {
        emailError.style.opacity = 1;
        emailError.innerHTML = "Please enter a valid email address.";
        hasError = true;
    }

    // --- PASSWORD VALIDATION ---
    if (password.length < 6 || password.length > 20) {
        passwordError.style.opacity = 1;
        passwordError.innerHTML = "Password must be between 6 and 20 characters.";
        hasError = true;
    }


    // --- CONFIRM PASSWORD ---
    if (confirmPassword !== password) {
        confirmPasswordError.style.opacity = 1;
        confirmPasswordError.innerHTML = "Passwords do not match.";
        hasError = true;
    }

    if (hasError) return;

    // --- Disable inputs during submission ---
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Registering...';
    form.style.opacity = 0.8;
    inputs.forEach(input => input.disabled = true);

    // --- Send data to backend ---
    fetch('/add_admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/'; // or your dashboard page
            } else {
                form.style.opacity = 1;
                inputs.forEach(input => input.disabled = false);
                if (data.error === 'invalid_name') {
                    nameError.style.opacity = 1;
                    nameError.innerHTML = data.message;
                } else if (data.error === 'invalid_email') {
                    emailError.style.opacity = 1;
                    emailError.innerHTML = data.message;
                } else if (data.error === 'invalid_password') {
                    passwordError.style.opacity = 1;
                    passwordError.innerHTML = data.message;
                } else {
                    Error.style.opacity = 1;
                    Error.innerHTML = data.message || "Registration failed.";
                }
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Something went wrong. Try again.');
        })
        .finally(() => {
            // Reset button
            button.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Register';
            form.style.opacity = 1;
            inputs.forEach(input => input.disabled = false);
        });
}
