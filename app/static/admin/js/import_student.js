function import_students() {
    const fileInput = document.getElementById('import-file');

    // Check if file is selected
    if (fileInput.files.length === 0) {
        alert("Please select a file first!");
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);  // send the actual file



    // Send request to Flask route `/view_excel`
    fetch('/add_students_as_import', {
        method: 'POST',
        body: formData  // important: FormData handles file uploads
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        return response.json();
    })
    .then(data => {
       
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
