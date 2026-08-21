export default function TypingIndicator() {
  return (
    <div className="flex gap-1.5 px-4 py-3 self-start">
      <span className="w-2 h-2 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '-0.32s' }}></span>
      <span className="w-2 h-2 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '-0.16s' }}></span>
      <span className="w-2 h-2 bg-brand-accent rounded-full animate-bounce"></span>
    </div>
  );
}