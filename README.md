# Average Pythia

A real-time multiplayer guessing game where players create questions with numeric answers and compete to guess the median value.

## Features

- Real-time multiplayer gameplay via WebSockets
- Doodle drawing for questions
- Optional timer mode
- Mobile-responsive design
- Player reconnection support

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python app.py
```

3. Open your browser to `http://localhost:5000`

### Testing

To test multiplayer functionality:
- Open the game in one browser window (create a game)
- Open another browser window or use your phone (join with the code)

## Deployment to Render

1. Push this repository to GitHub
2. Connect your GitHub repo to Render
3. Render will automatically detect the `render.yaml` configuration
4. Your app will be deployed with WebSocket support

## Game Flow

1. **Start Screen**: Create or join a game
2. **Invite**: Share QR code or game code with players
3. **Enter Questions**: All players create questions with optional doodles
4. **Answer**: Players answer each question in random order
5. **Results**: See who guessed closest to the median
6. **Leaderboard**: Track scores between questions
7. **Final Results**: Celebrate the "Power Pythia"!

## Technology Stack

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: Vanilla JavaScript + Tailwind CSS
- **Real-time**: Socket.IO
- **Deployment**: Render

## Project Structure

```
average_pythia/
├── app.py                    # Flask app + SocketIO events
├── game_manager.py           # Game logic and state management
├── config.py                 # Configuration
├── templates/
│   └── index.html            # Single-page application
├── static/
│   ├── css/style.css         # Custom styles
│   └── js/
│       ├── app.js            # Main app logic
│       ├── screens.js        # Screen rendering
│       └── canvas.js         # Doodle drawing
└── render.yaml               # Render deployment config
```
