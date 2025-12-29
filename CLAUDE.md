# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Average Pythia is a real-time multiplayer guessing game where players:
1. Create questions with numeric answers (optionally with doodles/images)
2. Answer each other's questions synchronously
3. Score points for guessing the median value
4. The player who guesses the most medians wins ("Average Pythia")

The game is in English despite the project documentation being in Swedish.

## Technology Stack

- **Backend**: Flask (Python) deployed on Render
- **Real-time Communication**: WebSockets for synchronized gameplay
- **Authentication**: Google Auth (implemented in phase 2)
- **Database**: Supabase (for user data and curated question sets)
- **Frontend**: Mobile-responsive web interface (no app installation required)

## Architecture Notes

### Game State Management
The game has distinct phases that all players move through synchronously:
- **Lobby phases**: Waiting for players to join, submit questions, or answer
- **Active phases**: Enter question, Reply to question, Present winner, Leaderboard, Final results
- **Role distinction**: Game starter has special permissions to force progression through "Start playing", "Present winner", and "Next" buttons

### WebSocket Communication Pattern
All players must be kept synchronized through game phases. The game starter can force progression at lobby screens even if not all players are ready, which requires careful state management.

### Median Calculation Rules
When player count is even, median is calculated as:
1. If one of the two middle values is closer to the mean of all answers, it wins
2. If both middle values are equidistant from the mean, both are winning answers
3. All players who guessed winning answer(s) get 1 point each

### Question Flow
- In "Normal game": Players create their own questions → random order determined → all answer each question in sequence
- In "Curated questions": Skip question creation, use pre-made question sets from database

## Development Phases

**Phase 1 (MVP)**:
- Normal game mode only
- No Google Auth (manual name entry)
- No curated questions
- No image upload (doodle drawing only)

**Phase 2**:
- Add Google Auth with persistent user data
- Add curated question sets
- Add image upload functionality

## Key Game Screens

Refer to "Projektbeskrivning Average Pythia.md" for detailed UI specifications for each screen. Critical screens include:
- Start screen → Start new game / Join game / Login
- Invite screen (QR code + unique code generation)
- Enter question (with doodle canvas)
- Game lobbies (3 variants for different waiting states)
- Reply to question (numeric input only)
- Present winner (sorted answers with median highlighted)
- Leaderboard (mid-game scores)
- Final results (with medal emojis for top 3)

## Important Constraints

- Player names must be unique within a game session
- Submit buttons are disabled until required input is provided
- Only numeric input (digits and decimal point) allowed for answers
- Logo display: Show logo.png if it exists, otherwise display text "Average Pythia"
