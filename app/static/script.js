// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const resultDiv = document.getElementById('result');
const statusMessage = document.getElementById('status-message');
const fileIdElement = document.getElementById('file-id');
const checkStatusBtn = document.getElementById('checkStatusBtn');
const submitBtn = document.getElementById('submitBtn');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    uploadForm.addEventListener('submit', handleFormSubmit);
    checkStatusBtn.addEventListener('click', checkStatus);
});

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
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
            
            // Store file ID in local storage
            saveToHistory(data.file_id, jobRole);
            
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
            const analysisResults = document.getElementById('analysis-results');
            
            switch(data.status) {
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
                    checkStatusBtn.classList.add('hidden');
                    
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
            
            // Update history item if needed
            updateHistoryItem(fileId, data.status);
        } else {
            statusMessage.textContent = "File not found. It may have been deleted.";
        }
    } catch (error) {
        console.error('Error:', error);
        statusMessage.textContent = "Error checking status. Please try again.";
    }
}

/**
 * Save analysis to history in local storage
 */
function saveToHistory(fileId, jobRole) {
    const history = JSON.parse(localStorage.getItem('resumeAnalysisHistory') || '[]');
    
    // Add to beginning of array
    history.unshift({
        id: fileId,
        jobRole,
        date: new Date().toISOString(),
        status: 'queued'
    });
    
    // Keep only latest 10 entries
    if (history.length > 10) {
        history.pop();
    }
    
    localStorage.setItem('resumeAnalysisHistory', JSON.stringify(history));
}

/**
 * Update history item status
 */
function updateHistoryItem(fileId, status) {
    const history = JSON.parse(localStorage.getItem('resumeAnalysisHistory') || '[]');
    
    const updatedHistory = history.map(item => {
        if (item.id === fileId) {
            return { ...item, status };
        }
        return item;
    });
    
    localStorage.setItem('resumeAnalysisHistory', JSON.stringify(updatedHistory));
}

/**
 * Display analysis results in the UI
 */
function displayAnalysisResults(result, fileName, jobRole) {
    const analysisResults = document.getElementById('analysis-results');
    analysisResults.classList.remove('hidden');
    
    // Set job role
    document.getElementById('job-role-display').textContent = jobRole || "Not specified";
    
    // Parse results and extract sections
    try {
        // Try to parse if result is a JSON string
        let resultData = result;
        if (typeof result === 'string') {
            try {
                resultData = JSON.parse(result);
            } catch (e) {
                // Not JSON, use as is
            }
        }
        
        // Extract sections using regular expressions if it's a string
        if (typeof resultData === 'string') {
            // Find strengths
            extractAndDisplaySection(resultData, 'strengths', 'strengths-content');
            
            // Find weaknesses
            extractAndDisplaySection(resultData, 'weaknesses', 'weaknesses-content');
            
            // Find changes needed
            extractAndDisplaySection(resultData, 'changes needed', 'changes-content');
            
            // Find summary
            extractAndDisplaySection(resultData, 'overall summary', 'summary-content');
        } else {
            // If it's an object with structured data
            if (resultData.strengths) {
                displayBulletPoints(resultData.strengths, 'strengths-content');
            }
            
            if (resultData.weaknesses) {
                displayBulletPoints(resultData.weaknesses, 'weaknesses-content');
            }
            
            if (resultData.changes || resultData.recommendations) {
                displayBulletPoints(resultData.changes || resultData.recommendations, 'changes-content');
            }
            
            if (resultData.summary) {
                displayBulletPoints(resultData.summary, 'summary-content');
            }
        }
    } catch (error) {
        console.error('Error displaying analysis:', error);
        document.getElementById('strengths-content').innerHTML = '<p>Error displaying results.</p>';
    }
}

/**
 * Extract section from text and display in HTML element
 */
function extractAndDisplaySection(text, sectionName, elementId) {
    const element = document.getElementById(elementId);
    
    // Create regex pattern for finding the section
    const pattern = new RegExp(`(?:${sectionName})[\\s\\:]+(.*?)(?=(?:strengths|weaknesses|improvements|recommendations|changes needed|overall|summary|conclusion|$))`, 'i');
    
    const matches = pattern.exec(text);
    if (matches && matches[1]) {
        let content = matches[1].trim();
        
        // Convert to bullet points if not already
        if (content.includes('•') || content.includes('-')) {
            // Already has bullet points, just format
            content = content.replace(/•/g, '•');
            content = content.split(/\n/).filter(line => line.trim()).map(line => {
                if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
                    return `<li>${line.trim().substring(1).trim()}</li>`;
                }
                return line;
            }).join('');
            element.innerHTML = `<ul>${content}</ul>`;
        } else {
            // Convert text to bullet points
            const points = content.split(/\.\s+/).filter(point => point.trim());
            const bullets = points.map(point => `<li>${point.trim()}</li>`).join('');
            element.innerHTML = `<ul>${bullets}</ul>`;
        }
    } else {
        element.innerHTML = '<p>No specific information available.</p>';
    }
}

/**
 * Display array or string as bullet points
 */
function displayBulletPoints(content, elementId) {
    const element = document.getElementById(elementId);
    
    if (Array.isArray(content)) {
        const bullets = content.map(point => `<li>${point}</li>`).join('');
        element.innerHTML = `<ul>${bullets}</ul>`;
    } else if (typeof content === 'string') {
        const points = content.split(/\.\s+/).filter(point => point.trim());
        const bullets = points.map(point => `<li>${point.trim()}</li>`).join('');
        element.innerHTML = `<ul>${bullets}</ul>`;
    } else {
        element.innerHTML = '<p>No specific information available.</p>';
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
    
    // Hide the analysis results section
    document.getElementById('analysis-results').classList.add('hidden');
}
