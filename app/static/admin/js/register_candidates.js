async function candidate_registration() {
    // Get form elements
    const name = document.getElementById('name').value.trim();
    const photo = document.getElementById('photo');
    const election = document.getElementById('election');
    const statement = document.getElementById('statement');

    // Error message elements
    const nameError = document.getElementById('name_error');
    const photoError = document.getElementById('photo_error');
    const electionError = document.getElementById('election_error');
    const statementError = document.getElementById('statement_error');

    // Alert boxes
    const succ_msg = document.getElementById('succ_msg');
    const err_msg = document.getElementById('err_msg');

    // Button & spinner
    const button = document.getElementById('submit_button');
    const spinner = document.getElementById('spinner');
    const buttonText = button.querySelector('.button-text');

    // Reset previous messages
    [succ_msg, err_msg, nameError, photoError, electionError, statementError].forEach(el => {
        el.classList.add('d-none');
        el.textContent = '';
    });

    // === VALIDATION ===
    let valid = true;

    const nameParts = name.split(' ').filter(Boolean);
    if (nameParts.length < 3 || nameParts.length > 4) {
        nameError.classList.remove('d-none');
        nameError.innerHTML = "Full name must contain 3–4 parts.";
        valid = false;
    } else if (!nameParts.every(part => /^[A-Za-z]{3,15}$/.test(part))) {
        nameError.classList.remove('d-none');
        nameError.innerHTML = "Each name part must be 3–15 alphabetic characters.";
       valid = false;
    }

    if (!photo.files[0]) {
        photoError.textContent = 'Candidate photo is required.';
        photoError.classList.remove('d-none');
        valid = false;
    }

    if (election.value === '') {
        electionError.textContent = 'Please select an election.';
        electionError.classList.remove('d-none');
        valid = false;
    }


    if (statement.value.trim() === '') {
        statementError.textContent = 'Statement is required.';
        statementError.classList.remove('d-none');
        valid = false;
    }

    if (!valid) return; // Stop if validation failed

    // === FORM DATA ===
    const formData = new FormData();
    formData.append('name', name);
    formData.append('photo', photo.files[0]);
    formData.append('election', election.value);
    formData.append('statement', statement.value.trim());

    // === DISABLE BUTTON ===
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Submitting...';

    try {
        const response = await fetch('/add_candidate', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            succ_msg.textContent = result.message || 'Candidate registered successfully!';
            succ_msg.classList.remove('d-none');

            // Reset form
            document.getElementById('candidate_form').reset();
        } else {
            err_msg.textContent = result.message || 'Failed to register candidate.';
            err_msg.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error:', error);
        err_msg.textContent = 'An unexpected error occurred.';
        err_msg.classList.remove('d-none');
    } finally {
        // Re-enable button
        button.disabled = false;
        spinner.classList.add('d-none');
        buttonText.textContent = 'Submit Form';
    }
}
