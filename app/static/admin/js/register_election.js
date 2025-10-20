function election_registration() {
    console.log("Submitting election form...");

    // Get form elements
    const form = document.getElementById('election_form');
    const succ_msg = document.getElementById('succ_msg');
    const err_msg = document.getElementById('err_msg');
    const spinner = document.getElementById('spinner');
    const button = document.getElementById('submit_button');
    const buttonText = button.querySelector('.button-text');

    // Input fields
    const name = document.getElementById('name');
    const start_date = document.getElementById('start_date');
    const end_date = document.getElementById('end_date');
    const photo = document.getElementById('photo');
    const description = document.getElementById('election_desc');

    // Error message containers
    const nameError = document.getElementById('name_error');
    const startDateError = document.getElementById('start_date_error');
    const endDateError = document.getElementById('end_date_error');
    const photoError = document.getElementById('photo_error');
    const descError = document.getElementById('election_desc_error');

    // Reset previous messages
    [succ_msg, err_msg, nameError, startDateError, endDateError, photoError, descError].forEach(el => {
        el.classList.add('d-none');
        el.textContent = '';
    });


    let hasError = false;

    // --- Validation ---
    if (!name.value) {
        nameError.textContent = "Election name is required.";
        nameError.classList.remove('d-none');
        hasError = true;
    }

    if (!start_date.value) {
        startDateError.textContent = "Start date is required.";
        startDateError.classList.remove('d-none');
        hasError = true;
    }

    if (!end_date.value) {
        endDateError.textContent = "End date is required.";
        endDateError.classList.remove('d-none');
        hasError = true;
    } else if (start_date.value && end_date.value && new Date(end_date.value) < new Date(start_date.value)) {
        endDateError.textContent = "End date cannot be earlier than start date.";
        endDateError.classList.remove('d-none');
        hasError = true;
    }


    if (!photo.files[0]) {
        photoError.textContent = 'election photo is required.';
        photoError.classList.remove('d-none');
        valid = false;
    }

    if (!description.value) {
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
    formData.append("name", name.value.trim());
    formData.append("start_date", start_date.value);
    formData.append("end_date", end_date.value);
    formData.append("election_desc", description.value);
    formData.append("photo", photo.files[0]);
    console.log(formData)
    // --- Send data to backend ---
    fetch('/add_election', {
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
