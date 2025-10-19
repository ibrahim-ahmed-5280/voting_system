async function candidate_update(id) {
    // Get form elements
    const name = document.getElementById('name' + id).value.trim();
    const photo = document.getElementById('photo' + id);
    const election = document.getElementById('election' + id);
    const statement = document.getElementById('statement' + id);

    // Error message elements
    const nameError = document.getElementById('name_error' + id);
    const photoError = document.getElementById('photo_error' + id);
    const electionError = document.getElementById('election_error' + id);
    const statementError = document.getElementById('statement_error' + id);

    // Alert boxes
    const succ_msg = document.getElementById('succ_msg' + id);
    const err_msg = document.getElementById('err_msg' + id);

    // Button & spinner
    const button = document.getElementById('submit_button' + id);
    const spinner = document.getElementById('spinner' + id);
    const buttonText = button.querySelector('.button-text');

    // Reset previous messages
    [succ_msg, err_msg, nameError, electionError, statementError].forEach(el => {
        el.classList.add('d-none');
        el.textContent = '';
    });

    // === VALIDATION ===
    let valid = true;

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
    formData.append('id', id);
    formData.append('name', name);
    // Only append photo if user selected a new file
    if (photo.files && photo.files.length > 0) {
        formData.append('photo', photo.files[0]);
    }
    formData.append('election', election.value);
    formData.append('statement', statement.value.trim());

    // === DISABLE BUTTON ===
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'updating...';

    try {
        const response = await fetch('/update_candidate_details', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            succ_msg.textContent = result.message || 'Candidate registered successfully!';
            succ_msg.classList.remove('d-none');

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

async function submit_candidate_status_change(id, event) {
    event.preventDefault(); // prevent form default behavior
    event.stopPropagation(); // prevent dropdown from closing

    // Get form elements
    const selectStatus = document.getElementById('select_status_' + id);
    const successMsg = document.getElementById('status_success_' + id);
    const errorMsg = document.getElementById('status_error_' + id);
    const btn = document.getElementById('statusSubmitBtn_' + id);
    const spinner = document.getElementById('statusSpinner_' + id);
    const btnText = document.getElementById('statusText_' + id);

    // Reset previous messages
    successMsg.textContent = '';
    errorMsg.textContent = '';

    // Get selected status
    const selectedStatus = selectStatus.value.trim();

    // Validate
    if (!selectedStatus) {
        errorMsg.textContent = 'Please select a status before submitting.';
        return;
    }

    // Disable button and show spinner
    btn.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = 'Submitting...';

    try {
        const response = await fetch('/change_candidate_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id,
                status: selectedStatus
            })
        });

        const data = await response.json();

        if (data.success) {
            successMsg.textContent = data.message || 'Candidate status updated successfully!';
            errorMsg.textContent = '';
        } else {
            errorMsg.textContent = data.message || 'Failed to update candidate status.';
            successMsg.textContent = '';
        }
    } catch (error) {
        console.error('Error:', error);
        errorMsg.textContent = 'An error occurred while updating the status.';
    } finally {
        // Re-enable button and hide spinner
        btn.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = 'Submit';
    }
}