import { useEffect, useState } from 'react';
import './App.css';
import mockQuestion from './mockQuestion.json';

function App() {
  const [questionData, setQuestionData] = useState(null);
  const [guess, setGuess] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadQuestion = async () => {
    setIsLoadingQuestion(true);
    setEvaluation(null);
    setGuess('');

    await new Promise((resolve) => {
      setTimeout(resolve, 300);
    });

    setQuestionData(mockQuestion.recipe);
    setIsLoadingQuestion(false);
  };

  const submitGuess = async () => {
    if (!guess.trim() || !questionData) {
      return;
    }

    setIsSubmitting(true);

    await new Promise((resolve) => {
      setTimeout(resolve, 300);
    });

    setEvaluation(mockQuestion.output);
    setIsSubmitting(false);
  };

  useEffect(() => {
    loadQuestion();
  }, []);

  return (
    <div className="app">
      <main className="card">
        <h1>Recipe Guesser</h1>

        <button type="button" onClick={loadQuestion} disabled={isLoadingQuestion}>
          {isLoadingQuestion ? 'Loading question...' : 'New Question'}
        </button>

        {questionData && (
          <div className="question">
            <img
              src={questionData.image_url}
              alt={questionData.details.title}
              className="recipe-image"
            />

            <label htmlFor="guess-input">Guess ingredients</label>
            <input
              id="guess-input"
              type="text"
              value={guess}
              onChange={(event) => setGuess(event.target.value)}
              placeholder="e.g. tomato, mozzarella, basil"
            />

            <button
              type="button"
              onClick={submitGuess}
              disabled={isSubmitting || !guess.trim()}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Guess'}
            </button>
          </div>
        )}

        {evaluation && (
          <section className="evaluation">
            <h2>Evaluation</h2>
            <p>
              <strong>Rating:</strong> {evaluation.rating}
            </p>
            <p>{evaluation.response}</p>

            <ul>
              {evaluation.ingredientsMap.map((item, index) => (
                <li key={`${item.correctIngredient}-${index}`}>
                  {item.accepted ? '✅' : '❌'} {item.correctIngredient}
                  {item.proposedIngredient ? ` → ${item.proposedIngredient}` : ' → no guess'}
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
