function login() {
    const form = document.getElementById('singin_form');
    const inputs = form.querySelectorAll('input, button');
    const email = document.getElementById('emailaddress').value.trim();
    const password = document.getElementById('password').value.trim();

    const emailError = document.getElementById('email_error');
    const passError = document.getElementById('pass_error');
    const button = form.querySelector('button');
    const spinner = document.getElementById('spinner');
    const buttonText = button.querySelector('.button-text');

    // Reset errors
    [emailError, passError].forEach(err => {
        err.style.opacity = 0;
        err.innerHTML = "";
    });

    let hasError = false;

    // --- EMAIL VALIDATION ---
    const emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!emailPattern.test(email)) {
        emailError.style.opacity = 1;
        emailError.innerHTML = "Please enter a valid email address.";
        hasError = true;
    }

    // --- PASSWORD VALIDATION ---
    if (!password || password.length < 4) {
        passError.style.opacity = 1;
        passError.innerHTML = "Password must be at least 4 characters.";
        hasError = true;
    }

    if (hasError) return;

    // --- Disable inputs during submission ---
    button.disabled = true;
    spinner.classList.remove('d-none');
    button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging...`;
    form.style.opacity = 0.8;
    inputs.forEach(input => input.disabled = true);

    // --- Send data to backend ---
    fetch('/login_admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
        .then(res => res.json())
        .then(data => {
            form.style.opacity = 1;
            inputs.forEach(input => input.disabled = false);

            if (data.success) {
                window.location.href = '/dashboard_admin';
            } else {
                if (data.error === 'invalid_email') {
                    emailError.style.opacity = 1;
                    emailError.innerHTML = data.message;
                } else if (data.error === 'invalid_pass') {
                    passError.style.opacity = 1;
                    passError.innerHTML = data.message;
                } else {
                    alert(data.message || "Login failed. Please try again.");
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
            button.innerHTML = `Log In`;
            form.style.opacity = 1;
            inputs.forEach(input => input.disabled = false);
        });
}
