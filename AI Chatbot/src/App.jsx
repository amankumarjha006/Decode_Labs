import { useState, useRef, useEffect } from 'react';
import { initGemini, sendMessage } from './lib/gemini';
import useChatHistory from './hooks/useChatHistory';
import ChatBubble from './components/ChatBubble';
import ChatInput from './components/ChatInput';
import TypingIndicator from './components/TypingIndicator';

function App() {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiKeyMissing, setApiKeyMissing] = useState(false);
  const { history, appendMessage } = useChatHistory();
  const messagesEndRef = useRef(null);
  const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

  useEffect(() => {
    if (!apiKey) {
      setApiKeyMissing(true);
    } else {
      try {
        initGemini(apiKey);
      } catch (err) {
        setError('Failed to initialize Gemini: ' + err.message);
      }
    }
  }, [apiKey]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, isLoading]);

  const handleSend = async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading || apiKeyMissing) return;

    setError(null);
    setIsLoading(true);
    setInputValue('');

    appendMessage('user', trimmedInput);

    try {
      const trimmedHistory = history.map(msg => ({
        role: msg.role,
        parts: [{ text: msg.parts[0].text }]
      }));

      const responseText = await sendMessage(trimmedHistory, trimmedInput);
      appendMessage('model', responseText);
    } catch (err) {
      let errorMessage = err.message;
      if (err.message.includes('400')) {
        errorMessage = 'Invalid request. Please check your input.';
      } else if (err.message.includes('401') || err.message.includes('API key')) {
        errorMessage = 'Invalid API key. Please check your .env file.';
      } else if (err.message.includes('429')) {
        errorMessage = 'Rate limit exceeded. Please try again later.';
      } else if (err.message.includes('network') || err.message.includes('fetch')) {
        errorMessage = 'Network error. Please check your connection.';
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (history.length > 0 && history[history.length - 1].role === 'user') {
      const lastUserMessage = history[history.length - 1].parts[0].text;
      setInputValue(lastUserMessage);
      setError(null);
    }
  };

  if (apiKeyMissing) {
    return (
      <div className="min-h-screen bg-brand-cream flex flex-col">
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-xl bg-white rounded-2xl shadow-lg p-8 text-center">
            <h1 className="text-3xl font-semibold text-brand-purple mb-6">Chatbot with Memory</h1>
            <div className="bg-brand-cream/50 rounded-xl p-6 text-left">
              <h2 className="text-xl font-medium text-gray-900 mb-4">Setup Required</h2>
              <p className="text-gray-600 mb-4">Please add your Gemini API key to a <code className="bg-white px-1.5 py-0.5 rounded text-sm font-mono">.env</code> file:</p>
              <ol className="list-decimal list-inside space-y-2 text-gray-600 mb-4">
                <li>Copy <code className="bg-white px-1.5 py-0.5 rounded text-sm font-mono">.env.example</code> to <code className="bg-white px-1.5 py-0.5 rounded text-sm font-mono">.env</code></li>
                <li>Add your API key: <code className="bg-white px-1.5 py-0.5 rounded text-sm font-mono">VITE_GEMINI_API_KEY=your_key_here</code></li>
                <li>Restart the development server</li>
              </ol>
              <p className="text-gray-600">Get an API key from <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-brand-purple hover:underline">Google AI Studio</a></p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-cream flex flex-col">
      <header className="bg-brand-purple text-white px-6 py-5 shadow-sm">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-2xl font-semibold">Chatbot with Memory</h1>
          <p className="text-brand-cream/80 text-sm mt-1">Powered by Gemini 3.5 Flash</p>
        </div>
      </header>

      <main className="flex-1 flex flex-col max-w-3xl w-full mx-auto">
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {history.length === 0 && !isLoading && (
            <div className="flex items-center justify-center h-full min-h-[300px]">
              <p className="text-gray-500 text-center px-4">Start a conversation — try asking "My name is Vipin"</p>
            </div>
          )}

          {history.map((message, index) => (
            <ChatBubble
              key={index}
              role={message.role}
              text={message.parts[0].text}
            />
          ))}

          {isLoading && (
            <TypingIndicator />
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center justify-between gap-4 mx-6 mb-4 animate-fade-in">
            <span className="text-sm">{error}</span>
            <button
              onClick={handleRetry}
              className="px-4 py-1.5 text-sm font-medium text-red-700 border border-red-300 rounded-full hover:bg-red-100 transition-colors flex-shrink-0"
            >
              Retry
            </button>
          </div>
        )}

        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          disabled={apiKeyMissing}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}

export default App;