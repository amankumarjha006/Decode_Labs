import { useState, useCallback } from 'react';
import { trimHistory } from '../lib/gemini';

const MAX_HISTORY_MESSAGES = 30;

export default function useChatHistory() {
  const [history, setHistory] = useState([]);

  const appendMessage = useCallback((role, text) => {
    const message = {
      role,
      parts: [{ text }]
    };
    setHistory(prev => {
      const updated = [...prev, message];
      return trimHistory(updated, MAX_HISTORY_MESSAGES);
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  return {
    history,
    appendMessage,
    clearHistory,
    setHistory
  };
}