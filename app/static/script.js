// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const resultDiv = document.getElementById('result');
const statusMessage = document.getElementById('status-message');
const fileIdElement = document.getElementById('file-id');
const checkStatusBtn = document.getElementById('checkStatusBtn');
const submitBtn = document.getElementById('submitBtn');
const fileInput = document.getElementById('file');
const fileError = document.getElementById('file-error');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    uploadForm.addEventListener('submit', handleFormSubmit);
    checkStatusBtn.addEventListener('click', checkStatus);

    // Add file input change event to validate file type
    fileInput.addEventListener('change', validateFileType);

    // Initial validation check in case a file is already selected (browser cache)
    validateFileType();
});

/**
 * Validate file type and show error if not PDF
 */
function validateFileType() {
    const file = fileInput.files[0];
    const fileGroup = fileInput.closest('.form-group');

    // Clear previous error state
    fileGroup.classList.remove('error');
    fileError.classList.add('hidden');
    submitBtn.disabled = false;

    if (file) {
        // Check if the file is a PDF
        const fileType = file.type;
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if (fileType !== 'application/pdf' && fileExtension !== 'pdf') {
            // Show error message
            fileGroup.classList.add('error');
            fileError.classList.remove('hidden');
            fileInput.value = ''; // Clear the file input
            submitBtn.disabled = true; // Disable the submit button
            return false;
        }
    }
    return true;
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    // Validate file type before proceeding
    if (!validateFileType()) {
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing...';

    const formData = new FormData(uploadForm);
    const jobRole = formData.get('job_role');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.file_id) {
            // Show results section with success message immediately
            resultDiv.classList.remove('hidden');

            // Hide processing elements
            const resultHeading = document.getElementById('result-heading');
            const resultLoader = document.getElementById('result-loader');

            resultHeading.textContent = "Analysis Complete";
            resultLoader.classList.add('hidden');
            checkStatusBtn.classList.add('hidden');
            fileIdElement.classList.add('hidden');
            // Display success message directly
            showSuccessMessage(jobRole);

            // Clear form
            uploadForm.reset();
        } else {
            alert('Error: ' + data.status || 'Failed to upload file.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading your resume. Please try again.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Analyze Resume';
    }
}

/**
 * Check status of analysis
 */
async function checkStatus() {
    const fileId = checkStatusBtn.dataset.fileId;

    if (!fileId) return;

    try {
        statusMessage.textContent = "Checking status...";

        const response = await fetch(`/${fileId}`);
        const data = await response.json();
        if (data.message === "File found") {
            let statusText = "";
            const resultHeading = document.getElementById('result-heading');
            const resultLoader = document.getElementById('result-loader');

            switch (data.status) {
                case "saving":
                    statusText = "Your file is being saved...";
                    break;
                case "queued":
                    statusText = "Your resume is in queue for analysis...";
                    break;
                case "processing":
                    statusText = "Analysis in progress...";
                    break;
                case "processed successfully":
                case "completed":
                    resultHeading.textContent = "Analysis Complete";
                    resultLoader.classList.add('hidden');
                    fileIdElement.classList.add('hidden');

                    // Show the success message using our function
                    showSuccessMessage(data.job_role);
                    break;
                case "failed":
                    statusText = "Analysis failed. Please try again.";
                    resultHeading.textContent = "Analysis Failed";
                    resultLoader.classList.add('hidden');
                    break;
                default:
                    statusText = `Status: ${data.status}`;
            }
            statusMessage.textContent = statusText;
        } else {
            statusMessage.textContent = "File not found. It may have been deleted.";
        }
    } catch (error) {
        console.error('Error:', error);
        statusMessage.textContent = "Error checking status. Please try again.";
    }
}





/**
 * Display the success message with the job role
 */
function showSuccessMessage(jobRole) {
    statusMessage.textContent = "Analysis completed! A detailed report has been sent to your email.";

    // Create success message element
    const successMessage = document.createElement('div');
    successMessage.className = 'success-message';
    successMessage.innerHTML = `
        <div class="success-icon">✓</div>
        <h3>Resume Successfully Analyzed</h3>
        <p>We've analyzed your resume for the <strong>${jobRole || 'specified'}</strong> position.</p>
        <p>A detailed report with strengths, weaknesses, and recommendations has been sent to your email.</p>
    `;

    // Replace any existing success message
    const existingMessage = document.querySelector('.success-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    // Add new message after the status message
    statusMessage.parentNode.insertBefore(successMessage, statusMessage.nextSibling);
}
