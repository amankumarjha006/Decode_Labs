# Chatbot with Memory

A React (Vite) single-page chat application that talks to the Google Gemini Flash API and maintains full conversational context across a live session — built as Project 1 of the DecodeLabs Generative AI Industrial Training Kit.

## Features

- Live chat interface powered by Gemini Flash
- Full conversational memory across turns (in-session, role/parts schema)
- Sliding-window truncation to stay within token limits
- Input validation to block empty/whitespace submissions
- Clean, responsive UI styled with Tailwind CSS

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure your API key**

   Copy the example env file:
   ```bash
   cp .env.example .env
   ```

   Then get a key from [Google AI Studio](https://aistudio.google.com/apikey) and add it to `.env`:
   ```
   VITE_GEMINI_API_KEY=your_api_key_here
   ```

3. **Run the dev server**
   ```bash
   npm run dev
   ```

## Sliding-Window Design

This application implements a sliding-window (FIFO) truncation strategy to keep the conversation history within the model's context window limits.

- `MAX_HISTORY_MESSAGES` is set to **30** (roughly 15 user/model pairs).
- Once history exceeds this limit, the **oldest messages are dropped in pairs** (user + model) rather than individually — this preserves conversational coherence and ensures a model response is never left dangling without its corresponding user prompt.
- This balances token budget constraints against contextual continuity: recent, relevant context is retained while stale history is discarded.

## Memory Test Checklist

Run these three turns in order to verify memory is actually working:

| Turn | Input | Expected Result |
|------|-------|------------------|
| 1 | `My name is Vipin` | Short acknowledgment |
| 2 | `Write a poem about tech` | Large output — deliberately stresses the context window |
| 3 | `What is my name?` | Model correctly answers **"Vipin"**, proving the sliding-window history preserved the fact despite the large intervening turn |

## Project Structure

```
src/
  App.jsx                  # Top-level layout, holds chat history state, orchestrates turns
  main.jsx                 # Entry point
  lib/
    gemini.js              # SDK client init, sendMessage(history), trimHistory(history, max)
  components/
    ChatBubble.jsx          # Renders a single message (role, text)
    ChatInput.jsx           # Textarea + send button, handles Enter/Shift+Enter
    TypingIndicator.jsx     # Small loading dots component
  hooks/
    useChatHistory.js       # Encapsulates history state + append/trim logic
  index.css                 # Global reset + Tailwind imports
```

## Known Limitations

- **Client-side only** — the API key is exposed in the browser bundle. A production version would proxy requests through a backend server to keep the key secret.
- **No persistence** — conversation history is lost on page refresh. A production app would use a database or `localStorage`.
- **No streaming** — responses are awaited in full before rendering. Streaming would improve perceived latency.

## Tech Stack

- React (Vite)
- Tailwind CSS
- Google Generative AI SDK (`@google/generative-ai`) — Gemini Flash
