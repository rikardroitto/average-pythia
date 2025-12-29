// Main application logic and SocketIO handling

const socket = io();
let gameCode = null;

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

socket.on('error', (data) => {
    alert(data.message);
});

socket.on('game_created', (data) => {
    gameCode = data.code;
    isHost = true;

    document.getElementById('game-code').textContent = data.code;
    document.getElementById('qr-code').src = data.qr_data;

    renderPlayersList(data.players, 'invite-players-list');
    showScreen('invite');
});

socket.on('game_joined', (data) => {
    gameCode = data.code;
    isHost = data.is_host;

    renderPlayersList(data.players, 'lobby-players-list');
    showScreen('lobby-waiting');
});

socket.on('player_joined', (data) => {
    renderPlayersList(data.players, 'invite-players-list');
    renderPlayersList(data.players, 'lobby-players-list');
});

socket.on('player_left', (data) => {
    renderPlayersList(data.players, 'invite-players-list');
    renderPlayersList(data.players, 'lobby-players-list');
});

socket.on('go_to_screen', (data) => {
    const screenName = data.screen;
    const screenData = data.data;

    switch (screenName) {
        case 'lobby-waiting':
            renderPlayersList(screenData.players || [], 'lobby-players-list');
            showScreen('lobby-waiting');
            break;

        case 'enter-question':
            showScreen('enter-question');
            break;

        case 'lobby-questions':
            renderReadyList(screenData.ready_players || [], 'questions-ready-list');
            showScreen('lobby-questions');
            break;

        case 'lobby-questions-waiting':
            renderReadyList(screenData.ready_players || [], 'questions-waiting-ready-list');
            showScreen('lobby-questions-waiting');
            break;

        case 'answer':
            displayQuestion(screenData.question);
            // Clear answer input for new question
            const answerInput = document.getElementById('answer-input');
            const submitAnswerBtn = document.getElementById('submit-answer-btn');
            if (answerInput) {
                answerInput.value = '';
                submitAnswerBtn.disabled = true;
            }
            showScreen('answer');
            // Show timer if enabled
            if (screenData.timer_enabled) {
                document.getElementById('timer-display').classList.remove('hidden');
            }
            break;

        case 'lobby-answers':
            renderReadyList(screenData.ready_players || [], 'answers-ready-list');
            showScreen('lobby-answers');
            break;

        case 'lobby-answers-waiting':
            renderReadyList(screenData.ready_players || [], 'answers-waiting-ready-list');
            showScreen('lobby-answers-waiting');
            break;

        case 'winner':
            displayWinnerQuestion(screenData.question);
            renderResults(screenData.sorted_results, 'results-list');
            document.getElementById('median-value').textContent = screenData.median;

            if (isHost) {
                document.getElementById('next-btn').classList.remove('hidden');
            }
            showScreen('winner');
            break;

        case 'leaderboard':
            renderLeaderboard(screenData.scores, 'leaderboard-list', false);
            if (isHost) {
                document.getElementById('continue-btn').classList.remove('hidden');
            }
            showScreen('leaderboard');
            break;

        case 'final':
            renderLeaderboard(screenData.final_scores, 'final-scores-list', true);
            showScreen('final');
            break;
    }
});

socket.on('player_ready', (data) => {
    renderReadyList(data.ready_players, 'questions-ready-list');
    renderReadyList(data.ready_players, 'questions-waiting-ready-list');
    renderReadyList(data.ready_players, 'answers-ready-list');
    renderReadyList(data.ready_players, 'answers-waiting-ready-list');
});

socket.on('timer_tick', (data) => {
    const timerDisplay = document.getElementById('timer-countdown');
    if (timerDisplay) {
        timerDisplay.textContent = data.seconds_left;

        // Add warning class when time is low
        const timerContainer = document.getElementById('timer-display');
        if (data.seconds_left <= 10) {
            timerContainer.classList.add('warning');
        } else {
            timerContainer.classList.remove('warning');
        }
    }
});

socket.on('timer_expired', () => {
    // Timer expired - host should auto-advance
    if (isHost) {
        if (currentScreen === 'answer') {
            showWinner();
        }
    }
});

// Game actions
function createGame() {
    const name = document.getElementById('host-name').value.trim();
    if (!name) {
        alert('Please enter your name');
        return;
    }

    const timerEnabled = document.getElementById('timer-enabled').checked;
    const timerSeconds = parseInt(document.getElementById('timer-seconds').value);

    socket.emit('create_game', {
        name: name,
        timer_enabled: timerEnabled,
        timer_seconds: timerSeconds
    });
}

function joinGame() {
    const code = document.getElementById('join-code').value.trim().toUpperCase();
    const name = document.getElementById('join-name').value.trim();

    if (!code || !name) {
        alert('Please enter game code and your name');
        return;
    }

    socket.emit('join_game', {
        code: code,
        name: name
    });
}

function startGame() {
    socket.emit('start_game');
}

function submitQuestion() {
    const text = document.getElementById('question-text').value.trim();
    if (!text) {
        alert('Please enter a question');
        return;
    }

    const doodle = getCanvasData();

    socket.emit('submit_question', {
        text: text,
        doodle: doodle
    });
}

function startAnswering() {
    socket.emit('start_answering');
}

function submitAnswer() {
    const answer = document.getElementById('answer-input').value.trim();
    if (!answer) {
        alert('Please enter an answer');
        return;
    }

    // Replace comma with period for proper decimal parsing
    const normalizedAnswer = answer.replace(',', '.');

    socket.emit('submit_answer', {
        answer: normalizedAnswer
    });
}

function showWinner() {
    socket.emit('show_winner');
}

function nextQuestion() {
    socket.emit('next_question');
}

function continueToNext() {
    socket.emit('continue_to_next');
}
