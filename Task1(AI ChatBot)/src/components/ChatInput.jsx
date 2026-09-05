export default function ChatInput({ value, onChange, onSend, disabled, isLoading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) {
        onSend();
      }
    }
  };

  const isEmpty = !value.trim();

  return (
    <div className="flex gap-3 p-4 bg-white border-t border-gray-200">
      <textarea
        className="flex-1 min-h-[48px] max-h-[150px] px-4 py-3 text-base leading-relaxed border border-gray-300 rounded-full focus:outline-none focus:ring-3 focus:ring-brand-purple/20 focus:border-brand-purple disabled:bg-gray-100 disabled:text-gray-500 resize-none placeholder:text-gray-400"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled || isLoading}
        placeholder={isLoading ? 'Waiting for response...' : 'Type a message... (Shift+Enter for new line)'}
        rows={1}
        aria-label="Chat input"
      />
      <button
        className={`w-12 h-12 rounded-full flex items-center justify-center text-white transition-all duration-200 flex-shrink-0 ${
          disabled || isEmpty || isLoading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-brand-purple hover:bg-brand-accent active:scale-95'
        }`}
        onClick={onSend}
        disabled={disabled || isEmpty || isLoading}
        aria-label="Send message"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>
  );
}