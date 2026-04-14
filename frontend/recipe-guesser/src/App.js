import { useEffect, useState } from 'react';
import './App.css';
import mockQuestion from './mockQuestion.json';

const TOTAL_ROUNDS = 5;
const MAX_ROUND_SCORE = 100;

function App() {
  const [questionData, setQuestionData] = useState(null);
  const [guess, setGuess] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentRound, setCurrentRound] = useState(1);
  const [roundRatings, setRoundRatings] = useState([]);
  const [isGameFinished, setIsGameFinished] = useState(false);

  const finalRating =
    roundRatings.length === TOTAL_ROUNDS
      ? roundRatings.reduce((sum, value) => sum + value, 0)
      : null;

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

  const startNewGame = () => {
    setCurrentRound(1);
    setRoundRatings([]);
    setIsGameFinished(false);
    loadQuestion();
  };

  const submitGuess = async () => {
    if (!guess.trim() || !questionData || evaluation || isGameFinished) {
      return;
    }

    setIsSubmitting(true);

    await new Promise((resolve) => {
      setTimeout(resolve, 300);
    });

    const roundEvaluation = mockQuestion.output;
    setEvaluation(roundEvaluation);

    const updatedRatings = [...roundRatings, roundEvaluation.rating];
    setRoundRatings(updatedRatings);

    if (updatedRatings.length === TOTAL_ROUNDS) {
      setIsGameFinished(true);
    }

    setIsSubmitting(false);
  };

  const goToNextRound = () => {
    if (isGameFinished) {
      return;
    }

    setCurrentRound((previousRound) => previousRound + 1);
    loadQuestion();
  };

  useEffect(() => {
    startNewGame();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app">
      <main className="card">
        <h1>Recipe Guesser</h1>
        <p>
          <strong>Round:</strong> {Math.min(currentRound, TOTAL_ROUNDS)} / {TOTAL_ROUNDS}
        </p>

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
              disabled={isSubmitting || !guess.trim() || Boolean(evaluation) || isLoadingQuestion}
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

            <table>
              <thead>
                <tr>
                  <th>Your guess</th>
                  <th>Correct ingredient</th>
                </tr>
              </thead>
              <tbody>
                {evaluation.ingredientsMap.map((item, index) => (
                  <tr key={`${item.correctIngredient}-${index}`}>
                    <td className={item.accepted ? 'accepted' : 'rejected'}>
                      {item.proposedIngredient || ''}
                    </td>
                    <td>{item.correctIngredient}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <p>
              <strong>Preparation:</strong> {questionData?.details?.preparation}
            </p>

            {!isGameFinished && (
              <button type="button" onClick={goToNextRound} disabled={isLoadingQuestion}>
                {isLoadingQuestion ? 'Loading next round...' : 'Next Round'}
              </button>
            )}

            {isGameFinished && (
              <div className="final-rating">
                <h3>
                  Final Rating: {finalRating} / {TOTAL_ROUNDS * MAX_ROUND_SCORE}
                </h3>
                <button type="button" onClick={startNewGame}>
                  Play Again
                </button>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
