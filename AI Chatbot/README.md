# Chatbot with Memory

A React (Vite) single-page chat application that talks to the Google Gemini Flash API and maintains full conversational context across a live session.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy `.env.example` to `.env` and add your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your key:
   ```
   VITE_GEMINI_API_KEY=your_api_key_here
   ```

3. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)

4. Start the development server:
   ```bash
   npm run dev
   ```

## Sliding-Window Design

This application implements a sliding-window (FIFO) truncation strategy to manage the conversation history within the model's context window limits. The `MAX_HISTORY_MESSAGES` constant (set to 30, roughly 15 user/model pairs) defines the maximum number of messages sent to the API. When the history exceeds this limit, the oldest messages are dropped in pairs (user + model) to preserve conversation coherence — never leaving a dangling model response without its corresponding user prompt. This approach balances token budget constraints with contextual continuity, ensuring the model retains recent, relevant context while discarding stale history.

## Memory Test Checklist

Copy-paste these three turns in order to verify memory works correctly:

1. **Turn 1**: `"My name is Vipin"` → Expect a short acknowledgment.
2. **Turn 2**: `"Write a poem about tech"` → Deliberately large output to stress the context window.
3. **Turn 3**: `"What is my name?"` → Model must correctly answer **"Vipin"**, proving the sliding-window history preserved the fact despite the large intervening turn.

## Known Limitations

- **Client-side only**: The API key is exposed in the browser. A production version would proxy requests through a backend server to keep the key secret.
- **No persistence**: Conversation history is lost on page refresh. A production app would use a database or localStorage.
- **No streaming**: Responses are waited on fully before rendering. Streaming would improve perceived latency.

## Project Structure

```
src/
  App.jsx                  # Top-level layout, holds chat history state, orchestrates turns
  main.jsx                 # Entry point
  lib/
    gemini.js              # SDK client init, sendMessage(history), trimHistory(history, max)
  components/
    ChatBubble.jsx         # Renders a single message (role, text)
    ChatInput.jsx          # Textarea + send button, handles Enter/Shift+Enter
    TypingIndicator.jsx    # Small loading dots component
  hooks/
    useChatHistory.js      # Encapsulates history state + append/trim logic
  index.css                # Global reset + Tailwind imports
```