document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('emailForm');
    const resultsSection = document.getElementById('results');
    const analysisResult = document.getElementById('analysisResult');
    const loadingIndicator = document.getElementById('loading');

    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = document.getElementById('email');
            const email = emailInput.value.trim();
            
            if (!email) {
                showAlert('Please enter a valid email address', 'error');
                return;
            }
            
            // Show loading and results section
            resultsSection.style.display = 'block';
            loadingIndicator.style.display = 'block';
            analysisResult.style.display = 'none';
            
            try {
                const response = await fetch('/api/analyze-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrf_token') || ''
                    },
                    body: JSON.stringify({ email })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to analyze email');
                }
                
                // Display the analysis result
                displayAnalysisResult(data);
                
            } catch (error) {
                console.error('Error:', error);
                showAlert('An error occurred while analyzing the email. Please try again.', 'error');
                resultsSection.style.display = 'none';
            } finally {
                loadingIndicator.style.display = 'none';
            }
        });
    }
    
    function displayAnalysisResult(data) {
        // Show the results container
        resultsSection.style.display = 'block';
        
        // Update company info
        const domain = data.company_domain;
        const linkedinUrl = data.linkedin_profile;
        const companyName = domain.replace(/^www\.|\..+$/g, '').replace(/\.(com|org|net|io|ai|co|uk|de|fr|it|es|nl|se|no|fi|dk|pl|be|at|ch)$/i, '');
        const formattedCompanyName = companyName
            .split(/[^a-zA-Z0-9]+/)
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
            
        document.getElementById('companyName').textContent = formattedCompanyName;
        
        // Set up website link
        const websiteUrl = domain.startsWith('http') ? domain : `https://${domain}`;
        const websiteLink = document.getElementById('companyWebsite');
        websiteLink.href = websiteUrl;
        
        // Set up LinkedIn link if available
        const linkedinLink = document.getElementById('linkedinLink');
        if (linkedinUrl) {
            linkedinLink.href = linkedinUrl;
            linkedinLink.style.display = 'inline-flex';
        } else {
            linkedinLink.style.display = 'none';
        }
        
        // Process and display topics
        const topicsList = document.getElementById('topicsList');
        topicsList.innerHTML = ''; // Clear any existing items
        
        if (data.cheat_sheet_bullets) {
            // Split by comma but respect quotes (handles commas within bullet points)
            const topics = data.cheat_sheet_bullets.split(/\|(?=(?:[^"]*"[^"]*")*[^"]*$)/)
                .map(topic => topic.trim())
                .filter(topic => topic.length > 0);
                
            topics.forEach(topic => {
                const li = document.createElement('li');
                li.textContent = topic;
                topicsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No topics available';
            topicsList.appendChild(li);
        }
        
        // Show the results section
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analysisResult').style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Function to safely parse JSON from Claude's response
    function parseClaudeResponse(text) {
        try {
            // Try to find JSON in the response
            const jsonStart = text.indexOf('{');
            const jsonEnd = text.lastIndexOf('}') + 1;
            if (jsonStart >= 0 && jsonEnd > jsonStart) {
                const jsonStr = text.substring(jsonStart, jsonEnd);
                return JSON.parse(jsonStr);
            }
            return null;
        } catch (e) {
            console.error('Error parsing response:', e);
            return null;
        }
    }
    
    function showAlert(message, type = 'info') {
        // Remove any existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        // Insert the alert before the form
        if (emailForm) {
            emailForm.parentNode.insertBefore(alertDiv, emailForm);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                alertDiv.style.opacity = '0';
                setTimeout(() => alertDiv.remove(), 300);
            }, 5000);
        }
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});
