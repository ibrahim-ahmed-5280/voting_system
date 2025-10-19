function teacher_registration() {
    const form = document.getElementById('teacher_form');
    const name = document.getElementById('name').value.trim();
    const teacherId = document.getElementById('teacher_id').value.trim();
    const button = document.getElementById('submit_button');
    const spinner = document.getElementById('spinner');
    const buttonText = button.querySelector('.button-text');

    const nameError = document.getElementById('name_error');
    const idError = document.getElementById('teacher_id_error');
    const succ_msg = document.getElementById('succ_msg');
    const err_msg = document.getElementById('err_msg');

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
    fetch('/add_teacher', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, teacher_id: teacherId })
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                succ_msg.classList.remove('d-none');
                succ_msg.innerHTML = data.message;
                console.log(data, succ_msg);
                form.reset(); // Uncomment if you want to clear the form after success
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

function import_teachers() {
    const form = document.getElementById('import_form');
    const fileInput = document.getElementById('import-file');
    const button = form.querySelector('.btn-success');
    const spinner = form.querySelector('#spinner');
    const buttonText = button.querySelector('.button-text');
    const icon_upload = document.getElementById('icon-uplooad')
    const succ_msg = document.getElementById('succ_msg_import');
    const err_msg = document.getElementById('err_msg_import');

    // --- Reset messages ---
    [succ_msg, err_msg].forEach(msg => {
        msg.innerHTML = "";
        msg.classList.add('d-none');
    });

    // --- Validate file selection ---
    if (fileInput.files.length === 0) {
        err_msg.classList.remove('d-none');
        err_msg.innerHTML = "Please select a file before uploading.";
        return;
    }

    // --- Prepare FormData ---
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // --- Disable button and show spinner ---
    button.disabled = true;
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Importing...';
    icon_upload.classList.add('d-none');
    // --- Send file to backend ---
    fetch('/add_teachers_as_import', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            console.log("Server response:", data);

            if (data.status === 'success' || data.success === true) {
                succ_msg.classList.remove('d-none');
                succ_msg.innerHTML = data.message || "teachers imported successfully!";

                // Optionally show preview (first 5 records)
                if (data.data && data.data.length > 0) {
                    console.table(data.data);
                }

            } else {
                err_msg.classList.remove('d-none');
                err_msg.innerHTML = data.message || "Something went wrong during import.";
            }
        })
        .catch(err => {
            console.error("Error:", err);
            err_msg.classList.remove('d-none');
            err_msg.innerHTML = "Network or server error. Please try again.";
        })
        .finally(() => {
            // --- Re-enable button and hide spinner ---
            button.disabled = false;
            spinner.classList.add('d-none');
            icon_upload.classList.remove('d-none');
            buttonText.textContent = 'Import teachers';
        });
}