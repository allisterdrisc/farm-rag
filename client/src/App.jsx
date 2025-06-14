import { useState } from 'react';
import { askFarmAgent } from './services';
import { QuestionForm } from './components/QuestionForm';
import { MessageBox } from './components/MessageBox';
import './App.css'

function App() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(false);
    setMessages((prev) => [...prev, { sender: 'user', text: question.trim() }]);
    setQuestion('');

    try {
      const response = await askFarmAgent(question);
      setMessages((prev) => [...prev, { sender: 'bot', text: response}]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const handleChange = (e) => {
    setQuestion(e.currentTarget.value);
  }

  return (
    <>
      <h1>Farmer Rag🥬</h1>
      <div className='chat-container'>
        <MessageBox messages={messages} loading={loading} error={error} />
        <QuestionForm onSubmit={handleSubmit} onChange={handleChange} question={question} />
      </div>
    </>
  )
}

export default App
