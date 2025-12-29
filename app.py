from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import qrcode
import io
import base64
import os
import time
from config import Config
import game_manager as gm

app = Flask(__name__)
app.config.from_object(Config)

# Cache buster - changes on each server restart
CACHE_BUSTER = str(int(time.time()))
socketio = SocketIO(app, cors_allowed_origins="*")


def get_base_url():
    """Get base URL for QR code generation"""
    # In production, use the actual domain
    if os.environ.get('RENDER'):
        service_name = os.environ.get('RENDER_SERVICE_NAME', 'average-pythia')
        return f"https://{service_name}.onrender.com"
    # Local development
    return request.host_url.rstrip('/')


def generate_qr_code(game_code: str) -> str:
    """Generate QR code as base64 image"""
    url = f"{get_base_url()}/?join={game_code}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"


@app.route('/')
def index():
    return render_template('index.html', v=CACHE_BUSTER)


@app.after_request
def add_header(response):
    """Add cache headers for static files"""
    if 'static' in request.path:
        response.cache_control.max_age = 31536000  # 1 year
        response.cache_control.public = True
    return response


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    gm.disconnect_player(request.sid)

    # Notify other players
    game = gm.get_game(request.sid)
    if game:
        players = gm.get_players_list(game["code"])
        emit('player_left', {'players': players}, room=game["code"], skip_sid=request.sid)


@socketio.on('create_game')
def handle_create_game(data):
    """Create a new game"""
    name = data.get('name', '').strip()
    timer_enabled = data.get('timer_enabled', False)
    timer_seconds = data.get('timer_seconds', 90)

    if not name:
        emit('error', {'message': 'Name is required'})
        return

    game_code = gm.create_game(name, timer_enabled, timer_seconds, request.sid)
    join_room(game_code)

    qr_data = generate_qr_code(game_code)

    emit('game_created', {
        'code': game_code,
        'qr_data': qr_data,
        'players': gm.get_players_list(game_code)
    })


@socketio.on('join_game')
def handle_join_game(data):
    """Join an existing game"""
    code = data.get('code', '').strip().upper()
    name = data.get('name', '').strip()

    if not code or not name:
        emit('error', {'message': 'Code and name are required'})
        return

    success, error = gm.join_game(code, name, request.sid)

    if not success:
        emit('error', {'message': error})
        return

    join_room(code)

    # Check if this was a reconnection
    game = gm.get_game(request.sid)
    if game:
        players = gm.get_players_list(code)

        # Send current game state to reconnecting player
        emit('game_joined', {
            'code': code,
            'players': players,
            'is_host': gm.is_host(request.sid, code)
        })

        # Notify others
        emit('player_joined', {'players': players}, room=code, skip_sid=request.sid)

        # If game is in progress, send them to the right screen
        if game["phase"] == "lobby":
            emit('go_to_screen', {'screen': 'lobby-waiting', 'data': {'players': players}})
        elif game["phase"] == "answering":
            question = gm.get_current_question(code)
            ready_players = gm.get_ready_players(code)
            if request.sid in game["players_ready"]:
                emit('go_to_screen', {
                    'screen': 'lobby-answers',
                    'data': {'ready_players': ready_players}
                })
            else:
                emit('go_to_screen', {
                    'screen': 'answer',
                    'data': {'question': question}
                })


@socketio.on('start_game')
def handle_start_game():
    """Host starts the game (lobby -> question entry)"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not gm.is_host(request.sid, game["code"]):
        emit('error', {'message': 'Only host can start the game'})
        return

    if len(game["players"]) < 2:
        emit('error', {'message': 'Need at least 2 players to start'})
        return

    game["phase"] = "questions"
    game["players_ready"] = set()

    emit('go_to_screen', {'screen': 'enter-question', 'data': {}}, room=game["code"])


@socketio.on('submit_question')
def handle_submit_question(data):
    """Player submits a question"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    text = data.get('text', '').strip()
    doodle = data.get('doodle', '')

    if not text:
        emit('error', {'message': 'Question text is required'})
        return

    gm.submit_question(game["code"], request.sid, text, doodle)
    ready_players = gm.get_ready_players(game["code"])

    # Host goes to lobby-questions, others go to lobby-questions-waiting
    if gm.is_host(request.sid, game["code"]):
        emit('go_to_screen', {
            'screen': 'lobby-questions',
            'data': {'ready_players': ready_players}
        })
    else:
        emit('go_to_screen', {
            'screen': 'lobby-questions-waiting',
            'data': {'ready_players': ready_players}
        })

    # Update ready status for all players
    emit('player_ready', {'ready_players': ready_players}, room=game["code"])


@socketio.on('start_answering')
def handle_start_answering():
    """Host starts answering phase"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not gm.is_host(request.sid, game["code"]):
        emit('error', {'message': 'Only host can start answering'})
        return

    gm.start_answering(game["code"])
    question = gm.get_current_question(game["code"])

    if question:
        emit('go_to_screen', {
            'screen': 'answer',
            'data': {'question': question}
        }, room=game["code"])

        # Start timer if enabled
        if game["settings"]["timer_enabled"]:
            game["timer_start"] = True
            socketio.start_background_task(run_timer, game["code"])


@socketio.on('submit_answer')
def handle_submit_answer(data):
    """Player submits an answer"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    try:
        answer = float(data.get('answer', 0))
    except (ValueError, TypeError):
        emit('error', {'message': 'Invalid answer format'})
        return

    gm.submit_answer(game["code"], request.sid, answer)
    ready_players = gm.get_ready_players(game["code"])

    # Host goes to lobby-answers, others go to lobby-answers-waiting
    if gm.is_host(request.sid, game["code"]):
        emit('go_to_screen', {
            'screen': 'lobby-answers',
            'data': {'ready_players': ready_players}
        })
    else:
        emit('go_to_screen', {
            'screen': 'lobby-answers-waiting',
            'data': {'ready_players': ready_players}
        })

    # Update ready status for all players
    emit('player_ready', {'ready_players': ready_players}, room=game["code"])


@socketio.on('show_winner')
def handle_show_winner():
    """Host shows winner of current question"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not gm.is_host(request.sid, game["code"]):
        emit('error', {'message': 'Only host can show winner'})
        return

    question = gm.get_current_question(game["code"])
    if not question:
        emit('error', {'message': 'No current question'})
        return

    # Check if points already awarded for this question
    if question.get("points_awarded", False):
        emit('error', {'message': 'Points already awarded for this question'})
        return

    winners, sorted_results, median = gm.calculate_winner(question["answers"])
    gm.award_points(game["code"], winners)

    # Mark points as awarded
    question["points_awarded"] = True

    # Reset flag to allow advancing to next question
    game["advanced_from_winner"] = False

    # Send to each player individually with their host status
    for player_sid in game["players"]:
        emit('go_to_screen', {
            'screen': 'winner',
            'data': {
                'question': question,
                'sorted_results': sorted_results,
                'winners': winners,
                'median': median,
                'is_host': player_sid == game["host_sid"]
            }
        }, room=player_sid)


@socketio.on('next_question')
def handle_next_question():
    """Host proceeds to next question or final results"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not gm.is_host(request.sid, game["code"]):
        emit('error', {'message': 'Only host can proceed'})
        return

    # Prevent double-click from advancing twice
    if game.get("advanced_from_winner"):
        return
    game["advanced_from_winner"] = True

    has_more = gm.advance_to_next_question(game["code"])

    if has_more:
        # Show leaderboard - send to each player with host status
        leaderboard = gm.get_leaderboard(game["code"])
        for player_sid in game["players"]:
            emit('go_to_screen', {
                'screen': 'leaderboard',
                'data': {
                    'scores': leaderboard,
                    'is_host': player_sid == game["host_sid"]
                }
            }, room=player_sid)
    else:
        # Show final results
        final_scores = gm.get_leaderboard(game["code"])
        emit('go_to_screen', {
            'screen': 'final',
            'data': {'final_scores': final_scores}
        }, room=game["code"])


@socketio.on('continue_to_next')
def handle_continue_to_next():
    """Host continues from leaderboard to next question"""
    game = gm.get_game(request.sid)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not gm.is_host(request.sid, game["code"]):
        emit('error', {'message': 'Only host can proceed'})
        return

    question = gm.get_current_question(game["code"])
    if question:
        emit('go_to_screen', {
            'screen': 'answer',
            'data': {'question': question}
        }, room=game["code"])

        # Start timer if enabled
        if game["settings"]["timer_enabled"]:
            game["timer_start"] = True
            socketio.start_background_task(run_timer, game["code"])


def run_timer(game_code: str):
    """Background task to run timer"""
    if game_code not in gm.games:
        return

    game = gm.games[game_code]
    if not game["settings"]["timer_enabled"]:
        return

    timer_seconds = game["settings"]["timer_seconds"]

    for seconds_left in range(timer_seconds, 0, -1):
        if not game.get("timer_start"):
            break
        socketio.emit('timer_tick', {'seconds_left': seconds_left}, room=game_code)
        socketio.sleep(1)

    if game.get("timer_start"):
        game["timer_start"] = False
        socketio.emit('timer_expired', {}, room=game_code)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
