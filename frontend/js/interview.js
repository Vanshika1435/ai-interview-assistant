const API = 'https://ai-interview-assistant-backend-v5hv.onrender.com'
const token = localStorage.getItem('token')

if (!token) window.location.href = 'index.html'

const interviewType = localStorage.getItem('interview_type') || 'HR'
const interviewTopic = localStorage.getItem('interview_topic') || ''

// Reuse the session already created by dashboard
let sessionId = parseInt(localStorage.getItem('session_id')) || null
let currentScore = 0
let questionCount = 0

document.getElementById('interview-title').textContent = `${interviewType} Interview`
document.getElementById('interview-subtitle').textContent = interviewTopic ? `Topic: ${interviewTopic}` : 'General Questions'

// Enter to send
document.getElementById('answer-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        sendAnswer()
    }
})

function addMessage(role, content) {
    const chat = document.getElementById('chat-area')
    const div = document.createElement('div')
    div.className = `message ${role}`
    div.innerHTML = `<div class="message-bubble">${content}</div>`
    chat.appendChild(div)
    chat.scrollTop = chat.scrollHeight
}

function addFeedback(score, feedback) {
    const chat = document.getElementById('chat-area')
    const div = document.createElement('div')
    div.style.cssText = 'max-width:75%;align-self:flex-end'
    div.innerHTML = `
        <div class="feedback-box">
            <div class="feedback-score">Score: ${score}/10</div>
            <div>${feedback}</div>
        </div>
    `
    chat.appendChild(div)
    chat.scrollTop = chat.scrollHeight
}

function showTyping() {
    const chat = document.getElementById('chat-area')
    const div = document.createElement('div')
    div.className = 'message ai'
    div.id = 'typing'
    div.innerHTML = `
        <div class="message-bubble typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `
    chat.appendChild(div)
    chat.scrollTop = chat.scrollHeight
}

function removeTyping() {
    const t = document.getElementById('typing')
    if (t) t.remove()
}

async function startSession() {
    // If dashboard already created a session, just show the first question
    const savedQuestion = localStorage.getItem('first_question')
    if (sessionId && savedQuestion) {
        localStorage.removeItem('first_question')   // consume it
        addMessage('ai', savedQuestion)
        return
    }

    // Fallback: create a new session (e.g. direct URL access)
    showTyping()
    try {
        const res = await fetch(`${API}/interview/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                interview_type: interviewType,
                topic: interviewTopic || null
            })
        })
        const data = await res.json()
        removeTyping()

        if (!res.ok) {
            addMessage('ai', 'Error starting interview. Please try again.')
            return
        }

        sessionId = data.session_id
        addMessage('ai', data.question || data.first_question)
    } catch (err) {
        removeTyping()
        addMessage('ai', 'Connection error. Make sure the server is running.')
    }
}

async function sendAnswer() {
    const input = document.getElementById('answer-input')
    const answer = input.value.trim()

    if (!answer || !sessionId) return

    addMessage('user', answer)
    input.value = ''
    input.style.height = 'auto'

    showTyping()

    try {
        const res = await fetch(`${API}/interview/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                session_id: sessionId,
                user_answer: answer
            })
        })
        const data = await res.json()
        removeTyping()

        if (!res.ok) {
            addMessage('ai', 'Error processing answer.')
            return
        }

        questionCount++
        currentScore = data.total_score
        document.getElementById('current-score').textContent = currentScore.toFixed(1)

        addFeedback(data.score, data.feedback)
        addMessage('ai', data.next_question)

    } catch (err) {
        removeTyping()
        addMessage('ai', 'Connection error. Try again.')
    }
}

async function endInterview() {
    if (!sessionId) {
        window.location.href = 'dashboard.html'
        return
    }

    try {
        await fetch(`${API}/interview/end/${sessionId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        })
    } catch (err) {}

    // Clear session keys
    localStorage.removeItem('session_id')
    localStorage.removeItem('first_question')

    alert(`Interview Complete!\nQuestions: ${questionCount}\nFinal Score: ${currentScore.toFixed(1)}/10`)
    window.location.href = 'dashboard.html'
}

// Start on page load
startSession()

// ── Voice Recording ──
let mediaRecorder = null
let audioChunks = []
let isRecording = false

async function toggleVoice() {
    if (!isRecording) startRecording()
    else stopRecording()
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder = new MediaRecorder(stream)
        audioChunks = []

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data)
        mediaRecorder.onstop = processVoiceToText

        mediaRecorder.start()
        isRecording = true

        const btn = document.getElementById('mic-btn')
        btn.textContent = '⏹️'
        btn.classList.add('recording')
    } catch (err) {
        alert('Microphone access denied. Please allow microphone access.')
    }
}

function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop()
        mediaRecorder.stream.getTracks().forEach(t => t.stop())
        isRecording = false

        const btn = document.getElementById('mic-btn')
        btn.textContent = '🎤'
        btn.classList.remove('recording')
    }
}

async function processVoiceToText() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
    const formData = new FormData()
    formData.append('audio', audioBlob, 'answer.wav')

    showTyping()

    try {
        const res = await fetch(`${API}/interview/speech-to-text`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        })
        const data = await res.json()
        removeTyping()

        if (!res.ok) {
            addMessage('ai', 'Voice transcription failed.')
            return
        }

        const input = document.getElementById('answer-input')
        input.value = data.transcribed_text
        input.focus()
    } catch(err) {
        removeTyping()
        addMessage('ai', 'Voice error. Please try again.')
    }
}