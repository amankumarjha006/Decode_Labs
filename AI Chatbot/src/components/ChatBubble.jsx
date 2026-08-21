export default function ChatBubble({ role, text }) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`max-w-[80%] px-4 py-3 rounded-2xl shadow-sm ${
        isUser
          ? 'bg-brand-purple text-white rounded-br-md'
          : 'bg-white text-gray-900 border border-gray-200 rounded-bl-md'
      }`}>
        <p className="whitespace-pre-wrap break-words leading-relaxed">{text}</p>
      </div>
    </div>
  );
}