// TutorAI+ Frontend JavaScript
let currentMode = 'auto';
let sessionId = generateSessionId();
let abortController = null;
let recognition = null;

// Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const stopBtn = document.getElementById('stopBtn');
const voiceBtn = document.getElementById('voiceBtn');
const newChatBtn = document.getElementById('newChatBtn');
const modeButtons = document.querySelectorAll('.mode-btn:not(.new-chat)');

// Initialize
function init() {
    setupEventListeners();
    setupVoiceRecognition();
    setActiveMode('auto');
}

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Setup event listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    stopBtn.addEventListener('click', stopGeneration);
    newChatBtn.addEventListener('click', newChat);
    voiceBtn.addEventListener('click', toggleVoiceInput);
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    messageInput.addEventListener('input', autoResizeTextarea);
    
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            setActiveMode(mode);
        });
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

// Set active mode
function setActiveMode(mode) {
    currentMode = mode;
    modeButtons.forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Remove welcome message if present
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message
    addMessage('user', message);
    
    // Show loading
    const loadingId = addLoadingMessage();
    
    // Show stop button, hide send button
    sendBtn.style.display = 'none';
    stopBtn.style.display = 'flex';
    
    // Create abort controller
    abortController = new AbortController();
    
    try {
        const response = await fetch('/api/respond', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                mode: currentMode,
                session_id: sessionId
            }),
            signal: abortController.signal
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const data = await response.json();
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        // Add assistant response
        addAssistantMessage(data);
        
    } catch (error) {
        removeLoadingMessage(loadingId);
        
        if (error.name === 'AbortError') {
            addMessage('assistant', 'Generation stopped by user.');
        } else {
            addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            console.error('Error:', error);
        }
    } finally {
        // Reset buttons
        sendBtn.style.display = 'flex';
        stopBtn.style.display = 'none';
        abortController = null;
    }
}

// Stop generation
function stopGeneration() {
    if (abortController) {
        abortController.abort();
    }
}

// Add user/assistant message
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (role === 'user') {
        contentDiv.textContent = content;
    } else {
        contentDiv.innerHTML = formatText(content);
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add assistant message with all features
function addAssistantMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Empathy line
    if (data.empathy_line) {
        const empathyDiv = document.createElement('div');
        empathyDiv.className = 'empathy-line';
        empathyDiv.textContent = data.empathy_line;
        contentDiv.appendChild(empathyDiv);
    }
    
    // Main content
    if (data.main_content) {
        const mainDiv = document.createElement('div');
        mainDiv.className = 'main-text';
        mainDiv.innerHTML = formatText(data.main_content);
        contentDiv.appendChild(mainDiv);
    }
    
    // Image
    if (data.image_url) {
        const imgContainer = document.createElement('div');
        imgContainer.className = 'image-container';
        const img = document.createElement('img');
        img.src = data.image_url;
        img.alt = 'Educational image';
        imgContainer.appendChild(img);
        contentDiv.appendChild(imgContainer);
    }
    
    // Quiz
    if (data.quiz) {
        const quizDiv = createQuizElement(data.quiz);
        contentDiv.appendChild(quizDiv);
    }
    
    // Suggested questions
    if (data.suggested_questions && data.suggested_questions.length > 0) {
        const questionsDiv = document.createElement('div');
        questionsDiv.className = 'suggested-questions';
        
        const title = document.createElement('h4');
        title.textContent = 'You might also ask:';
        questionsDiv.appendChild(title);
        
        data.suggested_questions.forEach(question => {
            const btn = document.createElement('button');
            btn.className = 'question-btn';
            btn.textContent = question;
            btn.addEventListener('click', () => {
                messageInput.value = question;
                sendMessage();
            });
            questionsDiv.appendChild(btn);
        });
        
        contentDiv.appendChild(questionsDiv);
    }
    
    // Speak button
    const speakBtn = document.createElement('button');
    speakBtn.className = 'speak-btn';
    speakBtn.textContent = '🔊 Speak Response';
    speakBtn.addEventListener('click', () => speakText(data.main_content));
    contentDiv.appendChild(speakBtn);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Create quiz element
function createQuizElement(quiz) {
    const quizDiv = document.createElement('div');
    quizDiv.className = 'quiz-container';
    
    const title = document.createElement('h3');
    title.className = 'quiz-title';
    title.textContent = quiz.title || 'Quiz';
    quizDiv.appendChild(title);
    
    quiz.questions.forEach((q, qIndex) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'quiz-question';
        
        const questionText = document.createElement('h5');
        questionText.textContent = `${qIndex + 1}. ${q.question}`;
        questionDiv.appendChild(questionText);
        
        q.options.forEach((option, oIndex) => {
            const optionBtn = document.createElement('button');
            optionBtn.className = 'quiz-option';
            optionBtn.textContent = option;
            optionBtn.addEventListener('click', () => {
                // Remove previous selection
                questionDiv.querySelectorAll('.quiz-option').forEach(btn => {
                    btn.classList.remove('selected');
                });
                optionBtn.classList.add('selected');
                
                // Show feedback
                if (oIndex === q.correct) {
                    optionBtn.style.background = 'var(--success)';
                    optionBtn.style.borderColor = 'var(--success)';
                    if (q.explanation) {
                        setTimeout(() => {
                            alert('✅ Correct! ' + q.explanation);
                        }, 100);
                    }
                } else {
                    optionBtn.style.background = 'var(--danger)';
                    optionBtn.style.borderColor = 'var(--danger)';
                    if (q.explanation) {
                        setTimeout(() => {
                            alert('❌ Incorrect. ' + q.explanation);
                        }, 100);
                    }
                }
            });
            questionDiv.appendChild(optionBtn);
        });
        
        quizDiv.appendChild(questionDiv);
    });
    
    return quizDiv;
}

// Add loading message
function addLoadingMessage() {
    const id = 'loading_' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = id;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = '<span></span><span></span><span></span>';
    
    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    return id;
}

// Remove loading message
function removeLoadingMessage(id) {
    const loadingMsg = document.getElementById(id);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// Format text (markdown-like)
function formatText(text) {
    // Escape HTML
    text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // Code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code>${code.trim()}</code></pre>`;
    });
    
    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Scroll to bottom with smooth animation
function scrollToBottom() {
    // Wait for content to be rendered
    setTimeout(() => {
        const scrollHeight = chatMessages.scrollHeight;
        const currentScroll = chatMessages.scrollTop + chatMessages.clientHeight;
        
        // Only scroll if we're not already at bottom (within 100px margin)
        if (scrollHeight - currentScroll > 100) {
            chatMessages.scrollTo({
                top: scrollHeight,
                behavior: 'smooth'
            });
        }
    }, 100); // Small delay to ensure content is rendered
}

// Voice Recognition Setup
function setupVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            voiceBtn.style.background = 'var(--danger)';
            voiceBtn.style.borderColor = 'var(--danger)';
        };
        
        recognition.onend = () => {
            voiceBtn.style.background = '';
            voiceBtn.style.borderColor = '';
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            messageInput.value = transcript;
            autoResizeTextarea();
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            voiceBtn.style.background = '';
            voiceBtn.style.borderColor = '';
        };
    } else {
        voiceBtn.style.display = 'none';
    }
}

// Toggle voice input
function toggleVoiceInput() {
    if (!recognition) return;
    
    if (voiceBtn.style.background) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

// Speak text
function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        // Remove markdown and HTML
        text = text.replace(/\*\*(.+?)\*\*/g, '$1');
        text = text.replace(/\*(.+?)\*/g, '$1');
        text = text.replace(/`([^`]+)`/g, '$1');
        text = text.replace(/```[\s\S]*?```/g, '');
        text = text.replace(/<[^>]*>/g, '');
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        
        window.speechSynthesis.speak(utterance);
    } else {
        alert('Text-to-speech is not supported in your browser.');
    }
}

// New chat
async function newChat() {
    if (confirm('Start a new chat? This will clear the conversation and memory.')) {
        try {
            await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            // Clear chat
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <h2>👋 Welcome to TutorAI+</h2>
                    <p>Your intelligent learning companion powered by AI</p>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <span class="feature-icon">📚</span>
                            <h3>Learn Anything</h3>
                            <p>Get personalized explanations on any topic</p>
                        </div>
                        <div class="feature-card">
                            <span class="feature-icon">💻</span>
                            <h3>Code Assistant</h3>
                            <p>Generate and understand code easily</p>
                        </div>
                        <div class="feature-card">
                            <span class="feature-icon">🎯</span>
                            <h3>Smart Quizzes</h3>
                            <p>Test your knowledge with AI quizzes</p>
                        </div>
                        <div class="feature-card">
                            <span class="feature-icon">📺</span>
                            <h3>Video Summaries</h3>
                            <p>Summarize YouTube videos instantly</p>
                        </div>
                    </div>
                </div>
            `;
            
            // Generate new session ID
            sessionId = generateSessionId();
            
        } catch (error) {
            console.error('Error resetting chat:', error);
        }
    }
}

// Initialize app
init();