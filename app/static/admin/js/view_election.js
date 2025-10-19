function election_registration(id) {
    console.log("Submitting election form...");

    // Get form elements
    const form = document.getElementById('election_form' + id);
    const succ_msg = document.getElementById('succ_msg' + id);
    const err_msg = document.getElementById('err_msg' + id);
    const spinner = document.getElementById('spinner' + id);
    const button = document.getElementById('submit_button' + id);
    const buttonText = button.querySelector('.button-text');

    // Input fields
    const nameInput = document.getElementById('name' + id);
    const startDateInput = document.getElementById('start_date' + id);
    const endDateInput = document.getElementById('end_date' + id);
    const photo = document.getElementById('photo' + id);
    const descInput = document.getElementById('election_desc' + id);

    // Error message containers
    const nameError = document.getElementById('name_error' + id);
    const startDateError = document.getElementById('start_date_error' + id)
    const endDateError = document.getElementById('end_date_error' + id)
    const photoError = document.getElementById('photo_error' + id);
    const descError = document.getElementById('election_desc_error' + id)
    // Reset previous messages
    const errorElements = [succ_msg, err_msg, nameError, startDateError, endDateError, photoError, descError].filter(el => el);

    // Reset previous messages safely
    errorElements.forEach(el => {
        el.classList.add('d-none');
        el.textContent = '';
    });

    // Read values
    const name = nameInput.value.trim();
    const start_date = startDateInput.value.trim();
    const end_date = endDateInput.value.trim();
    const election_desc = descInput.value.trim();
    console.log('start and end date',start_date,end_date);
    
    let hasError = false;

    // --- Validation ---
    if (!name) {
        nameError.textContent = "Election name is required.";
        nameError.classList.remove('d-none');
        hasError = true;
    }

    if (!start_date) {
        startDateError.textContent = "Start date is required.";
        startDateError.classList.remove('d-none');
        hasError = true;
    }

    if (!end_date) {
        endDateError.textContent = "End date is required.";
        endDateError.classList.remove('d-none');
        hasError = true;
    } else if (start_date && end_date && new Date(end_date) < new Date(start_date)) {
        endDateError.textContent = "End date cannot be earlier than start date.";
        endDateError.classList.remove('d-none');
        hasError = true;
    }


    if (!election_desc) {
        descError.textContent = "Description is required.";
        descError.classList.remove('d-none');
        hasError = true;
    }

    if (hasError) {
        console.log("Validation failed — check highlighted fields.");
        return;
    }

    // Disable button + show spinner
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Processing...';

    const formData = new FormData();
    formData.append("id", id);
    formData.append("name", name);
    formData.append("start_date", start_date);
    formData.append("end_date", end_date);
    formData.append("election_desc", election_desc);

    // Only append the photo if it exists
    if (photo.files && photo.files.length > 0) {
        formData.append("photo", photo.files[0]);
    }
    console.log(formData)
    // --- Send data to backend ---
    fetch('/update_election_details', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            console.log("Response:", data);

            if (data.success) {
                succ_msg.textContent = data.message || "Election added successfully!";
                succ_msg.classList.remove('d-none');
                form.reset();
            } else {
                err_msg.textContent = data.message || "Something went wrong.";
                err_msg.classList.remove('d-none');
            }
        })
        .catch(err => {
            console.error("Error:", err);
            err_msg.textContent = "Network error. Please try again.";
            err_msg.classList.remove('d-none');
        })
        .finally(() => {
            button.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Submit form';
        });
}

async function submit_election_status_change(id, event) {
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
    console.log(selectedStatus);
    try {
        const response = await fetch('/change_election_status', {
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
            successMsg.textContent = data.message || 'Election status updated successfully!';
            errorMsg.textContent = '';
        } else {
            errorMsg.textContent = data.message || 'Failed to update election status.';
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
