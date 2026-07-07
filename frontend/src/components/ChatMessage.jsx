function ChatMessage({ chat, darkMode }) {
  return (
    <div
      className={`p-6 rounded-2xl shadow-lg ${
        darkMode ? "bg-slate-900" : "bg-white"
      }`}
    >
      {/* User */}
      <div>
        <h2 className="text-lg font-bold text-blue-400">You</h2>
        <p className="mt-2">{chat.question}</p>
      </div>

      {/* AI */}
      <div className="mt-6">
        <h2 className="text-lg font-bold text-green-400">AI Assistant</h2>
        <p className="mt-2 whitespace-pre-wrap leading-7">{chat.answer}</p>
      </div>

      {/* Sources */}
      <div className="mt-6">
        <h3 className="font-semibold">Sources</h3>

        {chat.sources && chat.sources.length > 0 ? (
          <ul className="list-disc ml-6 mt-2 text-slate-400 space-y-1">
            {chat.sources.map((source, i) => {
              // Sources can be plain strings (legacy) or
              // { text, page } objects (page-aware citations).
              const text = typeof source === "string" ? source : source.text;
              const page = typeof source === "string" ? null : source.page;

              return (
                <li key={i}>
                  {text}
                  {page ? (
                    <span
                      className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                        darkMode
                          ? "bg-slate-800 text-slate-300"
                          : "bg-gray-200 text-slate-600"
                      }`}
                    >
                      Page {page}
                    </span>
                  ) : null}
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-slate-500 mt-2">No sources available</p>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
