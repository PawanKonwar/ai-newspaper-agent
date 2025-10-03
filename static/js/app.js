/**
 * AI Newspaper Agent - Frontend JavaScript
 * Handles form submission, API communication, and UI updates
 */

class NewspaperAgent {
    constructor() {
        this.form = document.getElementById('articleForm');
        this.topicInput = document.getElementById('topicInput');
        this.maxLengthSelect = document.getElementById('maxLength');
        this.generateBtn = document.getElementById('generateBtn');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.processingTimeSection = document.getElementById('processingTimeSection');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const topic = this.topicInput.value.trim();
        const maxLength = parseInt(this.maxLengthSelect.value);
        
        if (!topic) {
            this.showAlert('Please enter a topic for your article.', 'warning');
            return;
        }
        
        await this.generateArticle(topic, maxLength);
    }
    
    async generateArticle(topic, maxLength) {
        try {
            // Show loading state
            this.showLoadingState();
            
            // Make API request
            const response = await fetch('/generate-article', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topic,
                    max_length: maxLength
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Hide loading and show results
            this.hideLoadingState();
            this.displayResults(result);
            
        } catch (error) {
            console.error('Error generating article:', error);
            this.hideLoadingState();
            this.showAlert(`Error generating article: ${error.message}`, 'danger');
        }
    }
    
    showLoadingState() {
        this.generateBtn.disabled = true;
        this.generateBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Generating...';
        this.loadingSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.processingTimeSection.style.display = 'none';
        
        // Animate progress bar
        this.animateProgressBar();
    }
    
    hideLoadingState() {
        this.generateBtn.disabled = false;
        this.generateBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Generate Article';
        this.loadingSection.style.display = 'none';
    }
    
    animateProgressBar() {
        const progressBar = document.getElementById('progressBar');
        let progress = 0;
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            progressBar.style.width = progress + '%';
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 500);
        
        // Complete progress bar when results are shown
        setTimeout(() => {
            progressBar.style.width = '100%';
            clearInterval(interval);
        }, 2000);
    }
    
    displayResults(result) {
        // Update research stage
        this.updateStageResult('research', result.research_stage);
        
        // Update draft stage
        this.updateStageResult('draft', result.draft_stage);
        
        // Update final stage
        this.updateStageResult('final', result.final_stage);
        
        // Update processing time
        this.updateProcessingTime(result.processing_time);
        
        // Show results with animation
        this.resultsSection.style.display = 'block';
        this.processingTimeSection.style.display = 'block';
        
        // Add fade-in animation
        setTimeout(() => {
            this.resultsSection.classList.add('fade-in');
            this.processingTimeSection.classList.add('fade-in');
        }, 100);
        
        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    updateStageResult(stage, stageData) {
        const statusElement = document.getElementById(`${stage}Status`);
        const contentElement = document.getElementById(`${stage}Content`);
        const llmElement = document.getElementById(`${stage}LLM`);
        
        // Update status badge
        if (stageData.status === 'success') {
            statusElement.className = 'badge bg-success';
            statusElement.textContent = 'Success';
        } else if (stageData.status === 'error') {
            statusElement.className = 'badge bg-danger';
            statusElement.textContent = 'Error';
        } else {
            statusElement.className = 'badge bg-warning';
            statusElement.textContent = 'Skipped';
        }
        
        // Update LLM information
        if (stageData.llm_used) {
            llmElement.textContent = `Powered by ${stageData.llm_used}`;
        }
        
        // Update content
        let content = '';
        if (stage === 'research') {
            content = stageData.research_data || stageData.message;
        } else if (stage === 'draft') {
            content = stageData.draft_content || stageData.message;
        } else if (stage === 'final') {
            content = stageData.final_content || stageData.message;
        }
        
        // Format content for display
        contentElement.innerHTML = this.formatContent(content);
    }
    
    formatContent(content) {
        if (!content) return '<p class="text-muted">No content available</p>';
        
        // Convert line breaks to HTML
        content = content.replace(/\n/g, '<br>');
        
        // Wrap in paragraphs if it's a long text
        if (content.length > 200 && !content.includes('<br>')) {
            const sentences = content.split('. ');
            const paragraphs = [];
            let currentParagraph = '';
            
            for (let i = 0; i < sentences.length; i++) {
                currentParagraph += sentences[i];
                if (i < sentences.length - 1) currentParagraph += '. ';
                
                if (currentParagraph.length > 300 || i === sentences.length - 1) {
                    paragraphs.push(`<p>${currentParagraph}</p>`);
                    currentParagraph = '';
                }
            }
            
            return paragraphs.join('');
        }
        
        return `<p>${content}</p>`;
    }
    
    updateProcessingTime(time) {
        const timeElement = document.getElementById('processingTime');
        const formattedTime = time.toFixed(2);
        timeElement.textContent = `${formattedTime} seconds`;
    }
    
    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NewspaperAgent();
});

// Add some utility functions for better UX
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading state to form submission
    const form = document.getElementById('articleForm');
    if (form) {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
            }
        });
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.getElementById('articleForm');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });
});
