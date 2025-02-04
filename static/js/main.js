document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const videoContainer = document.querySelector('.video-container');
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startRecord = document.getElementById('startRecord');
    const stopRecord = document.getElementById('stopRecord');
    
    let mediaRecorder;
    let recordedChunks = [];
    
    // Initial bot message
    addMessage("Hi! I'm the RecruitEase chatbot. I'll help you with your job application. Let's start with your name. What should I call you?", 'bot');
    
    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            
            // Send to backend
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'bot');
                
                // Show video recording UI if message contains 'video'
                if (data.response.toLowerCase().includes('record')) {
                    videoContainer.classList.remove('hidden');
                    initializeVideo();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your message. Please try again.', 'bot');
            });
            
            userInput.value = '';
        }
    }
    
    // Add message to chat with animation
    function addMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'mb-4', 'p-3', 'rounded-lg', 'shadow-sm');
        
        if (type === 'user') {
            messageDiv.classList.add('user-message', 'text-white', 'ml-auto');
        } else {
            messageDiv.classList.add('bot-message', 'text-gray-800');
        }
        
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom with smooth animation
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add typing animation for bot messages
        if (type === 'bot') {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                messageDiv.style.opacity = '1';
            }, 100);
        }
    }
    
    // Initialize video recording
    async function initializeVideo() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            video.srcObject = stream;
            
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = function(event) {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = function() {
                const blob = new Blob(recordedChunks, { type: 'video/webm' });
                const formData = new FormData();
                formData.append('video', blob, 'recording.webm');
                
                // Upload the video
                fetch('/api/upload-video', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    addMessage('Video uploaded successfully! Your application is complete.', 'bot');
                    // Save candidate information
                    return fetch('/api/save-candidate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({})
                    });
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        addMessage(data.message, 'bot');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error uploading your video. Please try again.', 'bot');
                });
                
                // Reset recording
                recordedChunks = [];
                video.srcObject.getTracks().forEach(track => track.stop());
                videoContainer.classList.add('hidden');
            };
        } catch (err) {
            console.error('Error accessing camera:', err);
            addMessage('Error accessing camera. Please make sure you have granted camera permissions.', 'bot');
        }
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    startRecord.addEventListener('click', function() {
        mediaRecorder.start();
        startRecord.classList.add('hidden');
        stopRecord.classList.remove('hidden');
        addMessage('Recording started... Click "Stop Recording" when you\'re finished.', 'bot');
    });
    
    stopRecord.addEventListener('click', function() {
        mediaRecorder.stop();
        startRecord.classList.remove('hidden');
        stopRecord.classList.add('hidden');
    });
    
    // Focus input on load
    userInput.focus();
});
