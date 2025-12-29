// Screen management and rendering functions

let currentScreen = 'start';
let isHost = false;

function showScreen(screenName) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });

    // Show target screen
    const targetScreen = document.getElementById(`screen-${screenName}`);
    if (targetScreen) {
        targetScreen.classList.remove('hidden');
        currentScreen = screenName;

        // Initialize canvas if on enter-question screen
        if (screenName === 'enter-question') {
            setTimeout(initCanvas, 100);
        }
    }
}

function renderPlayersList(players, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    players.forEach(player => {
        const div = document.createElement('div');
        div.className = 'player-item';

        let displayName = player.name;
        if (player.is_host) {
            displayName += ' (Host)';
        }
        if (!player.connected) {
            displayName += ' (disconnected)';
            div.classList.add('player-disconnected');
        }

        div.textContent = displayName;
        container.appendChild(div);
    });
}

function renderReadyList(readyPlayers, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    if (readyPlayers.length === 0) {
        container.innerHTML = '<p class="text-gray-500">None yet...</p>';
        return;
    }

    readyPlayers.forEach(playerName => {
        const div = document.createElement('div');
        div.className = 'player-item player-ready';
        div.innerHTML = `<span>✓ ${playerName}</span>`;
        container.appendChild(div);
    });
}

function renderResults(sortedResults, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    sortedResults.forEach(result => {
        const div = document.createElement('div');
        div.className = 'player-item';
        if (result.is_winner) {
            div.classList.add('winner-item');
        }

        const text = result.is_winner
            ? `⭐ ${result.name}: ${result.answer}`
            : `${result.name}: ${result.answer}`;

        div.textContent = text;
        container.appendChild(div);
    });
}

function renderLeaderboard(scores, containerId, showMedals = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    // Calculate medals for tied scores
    const medals = {};
    if (showMedals && scores.length > 0) {
        let medalsGiven = 0;
        let position = 1;

        // Group scores by unique values
        const uniqueScores = [];
        let lastScore = null;
        scores.forEach(scoreData => {
            if (scoreData.score !== lastScore) {
                uniqueScores.push({
                    score: scoreData.score,
                    players: [scoreData.name]
                });
                lastScore = scoreData.score;
            } else {
                uniqueScores[uniqueScores.length - 1].players.push(scoreData.name);
            }
        });

        // Assign medals
        for (const group of uniqueScores) {
            if (medalsGiven >= 3) break;

            let medal = null;
            if (position === 1) medal = '🥇';
            else if (position === 2) medal = '🥈';
            else if (position === 3) medal = '🥉';
            else break;

            // Give medal to all players in this score group
            group.players.forEach(name => {
                medals[name] = medal;
            });

            medalsGiven += group.players.length;
            position += group.players.length;
        }
    }

    scores.forEach((scoreData) => {
        const div = document.createElement('div');
        div.className = 'player-item';

        let text = '';
        if (medals[scoreData.name]) {
            text = `${medals[scoreData.name]} ${scoreData.name}: ${scoreData.score} points`;
        } else {
            text = `${scoreData.name}: ${scoreData.score} points`;
        }

        div.textContent = text;
        container.appendChild(div);
    });
}

function displayQuestion(question) {
    // Set question text
    const textDisplay = document.getElementById('question-text-display');
    if (textDisplay) {
        textDisplay.textContent = question.text;
    }

    // Set doodle image
    const doodleImg = document.getElementById('question-doodle');
    if (doodleImg && question.doodle) {
        doodleImg.src = question.doodle;
        doodleImg.classList.remove('hidden');
    } else if (doodleImg) {
        doodleImg.classList.add('hidden');
    }
}

function displayWinnerQuestion(question) {
    const textDisplay = document.getElementById('winner-question-text');
    if (textDisplay) {
        textDisplay.textContent = question.text;
    }

    const doodleImg = document.getElementById('winner-question-doodle');
    if (doodleImg && question.doodle) {
        doodleImg.src = question.doodle;
        doodleImg.classList.remove('hidden');
    } else if (doodleImg) {
        doodleImg.classList.add('hidden');
    }
}

// Input validation
document.addEventListener('DOMContentLoaded', () => {
    // Timer toggle
    const timerEnabled = document.getElementById('timer-enabled');
    const timerSettings = document.getElementById('timer-settings');
    const timerSlider = document.getElementById('timer-seconds');
    const timerValue = document.getElementById('timer-value');

    if (timerEnabled && timerSettings) {
        timerEnabled.addEventListener('change', () => {
            if (timerEnabled.checked) {
                timerSettings.classList.remove('hidden');
            } else {
                timerSettings.classList.add('hidden');
            }
        });
    }

    if (timerSlider && timerValue) {
        timerSlider.addEventListener('input', () => {
            timerValue.textContent = timerSlider.value;
        });
    }

    // Question text validation
    const questionText = document.getElementById('question-text');
    const submitQuestionBtn = document.getElementById('submit-question-btn');

    if (questionText && submitQuestionBtn) {
        questionText.addEventListener('input', () => {
            submitQuestionBtn.disabled = questionText.value.trim() === '';
        });
    }

    // Answer validation (numeric only)
    const answerInput = document.getElementById('answer-input');
    const submitAnswerBtn = document.getElementById('submit-answer-btn');

    if (answerInput && submitAnswerBtn) {
        answerInput.addEventListener('input', (e) => {
            // Allow only numbers, minus sign, and decimal point/comma
            const value = e.target.value;
            const isValid = /^-?[0-9]*[.,]?[0-9]*$/.test(value) && value !== '' && value !== '-' && value !== '.' && value !== ',';
            submitAnswerBtn.disabled = !isValid;
        });
    }

    // Try to load logo, fallback to text
    const logo = document.getElementById('logo');
    const logoText = document.getElementById('logo-text');

    if (logo) {
        logo.addEventListener('load', () => {
            logo.classList.remove('hidden');
            if (logoText) logoText.classList.add('hidden');
        });

        logo.addEventListener('error', () => {
            logo.classList.add('hidden');
            if (logoText) logoText.classList.remove('hidden');
        });
    }

    // Check for join code in URL
    const urlParams = new URLSearchParams(window.location.search);
    const joinCode = urlParams.get('join');
    if (joinCode) {
        document.getElementById('join-code').value = joinCode;
        showScreen('join-name');
    }
});
