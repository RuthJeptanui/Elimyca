// static/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // Basic form validation (optional)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add any custom validation if needed
        });
    });

    // Render chart if on match_results page
    const chartCanvas = document.getElementById('tutorChart');
    if (chartCanvas && typeof tutorsData !== 'undefined') {
        const labels = tutorsData.map(t => t.name);
        const currentLoads = tutorsData.map(t => t.current_load);
        const availabilities = tutorsData.map(t => t.availability);

        new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Current Load',
                        data: currentLoads,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Availability',
                        data: availabilities,
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});


        let typingTimer;
        const typingDelay = 1000; // 1 second delay after user stops typing
        
        document.getElementById('needs_description').addEventListener('input', function() {
            const text = this.value;
            const typingIndicator = document.querySelector('.typing-indicator');
            const aiSuggestions = document.getElementById('aiSuggestions');
            
            // Clear previous timer
            clearTimeout(typingTimer);
            
            if (text.length > 10) {
                typingIndicator.style.display = 'block';
                aiSuggestions.style.display = 'none';
                
                // Set new timer
                typingTimer = setTimeout(() => {
                    getSuggestions(text);
                }, typingDelay);
            } else {
                typingIndicator.style.display = 'none';
                aiSuggestions.style.display = 'none';
            }
        });
        
        function getSuggestions(text) {
            fetch('/api/suggest_subjects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                displaySuggestions(data.suggestions);
                analyzeSentiment(text);
                document.querySelector('.typing-indicator').style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                document.querySelector('.typing-indicator').style.display = 'none';
            });
        }
        
        function displaySuggestions(suggestions) {
            const suggestionTags = document.getElementById('suggestionTags');
            const aiSuggestions = document.getElementById('aiSuggestions');
            
            if (suggestions.length > 0) {
                suggestionTags.innerHTML = '';
                suggestions.forEach(subject => {
                    const tag = document.createElement('span');
                    tag.className = 'suggestion-tag';
                    tag.textContent = subject;
                    tag.onclick = () => addSubjectToDescription(subject);
                    suggestionTags.appendChild(tag);
                });
                aiSuggestions.style.display = 'block';
            } else {
                aiSuggestions.style.display = 'none';
            }
        }
        
        function addSubjectToDescription(subject) {
            const textarea = document.getElementById('needs_description');
            const currentText = textarea.value;
            
            // Check if subject is already mentioned
            if (!currentText.toLowerCase().includes(subject.toLowerCase())) {
                textarea.value = currentText + (currentText.endsWith('.') || currentText.endsWith(' ') ? '' : ' ') + subject + ' ';
                textarea.focus();
                
                // Trigger suggestions update
                getSuggestions(textarea.value);
            }
        }
        
        function analyzeSentiment(text) {
            const sentimentIndicator = document.getElementById('sentimentIndicator');
            
            // Simple client-side sentiment analysis for demo
            const urgentWords = ['urgent', 'help', 'struggling', 'difficult', 'hard', 'confused', 'lost', 'failing', 'exam', 'test', 'deadline'];
            const positiveWords = ['learn', 'improve', 'understand', 'master', 'excel', 'achieve', 'goal'];
            
            const textLower = text.toLowerCase();
            const urgentCount = urgentWords.filter(word => textLower.includes(word)).length;
            const positiveCount = positiveWords.filter(word => textLower.includes(word)).length;
            
            let sentimentClass, sentimentText, sentimentIcon;
            
            if (urgentCount > positiveCount) {
                sentimentClass = 'sentiment-negative';
                sentimentText = 'High urgency detected - we\'ll prioritize finding you immediate help';
                sentimentIcon = 'fas fa-exclamation-triangle';
            } else if (positiveCount > 0) {
                sentimentClass = 'sentiment-positive';
                sentimentText = 'Great learning attitude detected - we\'ll find tutors who match your goals';
                sentimentIcon = 'fas fa-smile';
            } else {
                sentimentClass = 'sentiment-neutral';
                sentimentText = 'We\'ll find tutors based on your subject needs';
                sentimentIcon = 'fas fa-info-circle';
            }
            
            sentimentIndicator.className = `sentiment-indicator ${sentimentClass}`;
            sentimentIndicator.innerHTML = `<i class="${sentimentIcon} me-2"></i>${sentimentText}`;
            sentimentIndicator.style.display = 'block';
        }
        
        // Form submission with loading state
        document.getElementById('studentForm').addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>AI is finding your perfect tutor...';
            submitBtn.disabled = true;
        });
    

        
        // let typingTimer;
        // const typingDelay = 1000;
        
        document.getElementById('expertise').addEventListener('input', function() {
            const text = this.value;
            const typingIndicator = document.querySelector('.typing-indicator');
            const aiSuggestions = document.getElementById('aiSuggestions');
            
            clearTimeout(typingTimer);
            
            if (text.length > 10) {
                typingIndicator.style.display = 'block';
                aiSuggestions.style.display = 'none';
                
                typingTimer = setTimeout(() => {
                    getSuggestions(text);
                }, typingDelay);
            } else {
                typingIndicator.style.display = 'none';
                aiSuggestions.style.display = 'none';
            }
        });
        
        function getSuggestions(text) {
            fetch('/api/suggest_subjects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                displaySuggestions(data.suggestions);
                document.querySelector('.typing-indicator').style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                document.querySelector('.typing-indicator').style.display = 'none';
            });
        }
        
        function displaySuggestions(suggestions) {
            const suggestionTags = document.getElementById('suggestionTags');
            const aiSuggestions = document.getElementById('aiSuggestions');
            
            if (suggestions.length > 0) {
                suggestionTags.innerHTML = '';
                suggestions.forEach(subject => {
                    const tag = document.createElement('span');
                    tag.className = 'suggestion-tag';
                    tag.textContent = subject;
                    tag.onclick = () => addSubjectToExpertise(subject);
                    suggestionTags.appendChild(tag);
                });
                aiSuggestions.style.display = 'block';
            } else {
                aiSuggestions.style.display = 'none';
            }
        }
        
        function addSubjectToExpertise(subject) {
            const textarea = document.getElementById('expertise');
            const currentText = textarea.value;
            
            if (!currentText.toLowerCase().includes(subject.toLowerCase())) {
                textarea.value = currentText + (currentText.endsWith('.') || currentText.endsWith(' ') ? '' : ' ') + subject + ' ';
                textarea.focus();
                getSuggestions(textarea.value);
            }
        }
        
        document.getElementById('tutorForm').addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing Registration & Payment...';
            submitBtn.disabled = true;
        });
    

    



       
    