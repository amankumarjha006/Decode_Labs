import { GoogleGenerativeAI } from '@google/generative-ai';

const MAX_HISTORY_MESSAGES = 20;

let genAI = null;
let model = null;

export function initGemini(apiKey) {
  if (!apiKey) {
    throw new Error('Gemini API key is required');
  }
  genAI = new GoogleGenerativeAI(apiKey);
  model = genAI.getGenerativeModel({ model: 'gemini-3.5-flash' });
  
  return model;
}

export function getModel() {
  if (!model) {
    throw new Error('Gemini not initialized. Call initGemini() first.');
  }
  return model;
}

export function trimHistory(history, maxLength = MAX_HISTORY_MESSAGES) {
  if (history.length <= maxLength) {
    return history;
  }

  const excess = history.length - maxLength;
  let trimCount = excess;

  if (trimCount % 2 !== 0) {
    trimCount += 1;
  }

  const trimmed = history.slice(trimCount);

  console.log(`Trimmed ${trimCount} oldest messages, history now ${trimmed.length} entries`);

  return trimmed;
}

export async function sendMessage(history, userMessage) {
  const currentModel = getModel();

  const chat = currentModel.startChat({
    history: history.map(msg => ({
      role: msg.role,
      parts: [{ text: msg.parts[0].text }]
    })),
    generationConfig: {
      maxOutputTokens: 2048,
      temperature: 0.7,
    },
  });

  const result = await chat.sendMessage(userMessage);
  const response = result.response;
  return response.text();
}