export const QuestionForm = ({ onSubmit, onChange, question }) => {
  const getRandomQuestion = () => {
    const questions = [
      'How much profit did beets make?',
      'What was the most cost-efficient crop?',
      'How did carrots do?',
      'Did we grow cabbage?',
      'Was kale a successful crop?',
      'What was the most profitable crop?',
    ]

    const randomIdx = Math.floor(Math.random() * questions.length);
    return questions[randomIdx];
  };

  const handleRandomQuestion = () => {
    const randomQuestion = getRandomQuestion();
    onChange({ currentTarget: { value: randomQuestion }});
  };

  return (
    <form className='question-form' onSubmit={onSubmit}>
      <textarea className='question-input' rows={3} placeholder='Ask about your farm data...' value={question} onChange={(e) => onChange(e)}/>
      <button type='button' onClick={handleRandomQuestion}>Generate Sample Question</button>
      <button type='submit'>Send</button>
    </form>
  );
};