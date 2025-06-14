export const MessageBox = ({ messages, loading, error}) => {
  return (
    <div className='message-list'>
      {messages.map((message, idx) => (
        <div key={idx} className={`message-bubble ${message.sender === 'user' ? 'user' : 'bot'}`}>
          {message.sender === 'bot' ? `🧑‍🌾: ${message.text}` : message.text}
        </div>
      ))}

      {loading && (
        <div className='message-bubble bot loading'>
            🕓 Searching your farm data…
        </div>
      )}

      {error && (
        <div className="message-bubble bot error">
          ❗ {error}
        </div>
      )}
    </div>
  );
};