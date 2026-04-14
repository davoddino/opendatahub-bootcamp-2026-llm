import { useEffect, useState } from 'react';
import './App.css';
import mockQuestion from './mockQuestion.json';

const TOTAL_ROUNDS = 5;
const MAX_ROUND_SCORE = 100;
const SAVED_RECIPES_KEY = 'recipe-guesser-saved-recipes';
const API_BASE_URL = 'http://127.0.0.1:8000';

const normalizeRoundScore = (rating) => {
  if (!Number.isFinite(rating)) {
    return 0;
  }

  if (rating <= 10) {
    return Math.max(0, Math.min(100, rating * 10));
  }

  return Math.max(0, Math.min(100, rating));
};

function App() {
  const [questionData, setQuestionData] = useState(null);
  const [guess, setGuess] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentRound, setCurrentRound] = useState(1);
  const [roundRatings, setRoundRatings] = useState([]);
  const [isGameFinished, setIsGameFinished] = useState(false);
  const [currentPage, setCurrentPage] = useState('game');
  const [savedRecipes, setSavedRecipes] = useState(() => {
    const storedRecipes = localStorage.getItem(SAVED_RECIPES_KEY);
    if (!storedRecipes) {
      return [];
    }

    try {
      return JSON.parse(storedRecipes);
    } catch {
      return [];
    }
  });

  const finalRating =
    roundRatings.length === TOTAL_ROUNDS
      ? roundRatings.reduce((sum, value) => sum + value, 0)
      : null;

  const isCurrentRecipeSaved = Boolean(
    questionData && savedRecipes.some((recipe) => recipe.id === questionData.id)
  );

  const loadQuestion = async () => {
    setIsLoadingQuestion(true);
    setEvaluation(null);
    setGuess('');

    try {
      const response = await fetch(`${API_BASE_URL}/sendnewrequest?language=it`);
      if (!response.ok) {
        throw new Error('Unable to load question from server.');
      }

      const payload = await response.json();
      setQuestionData(payload.recipe);
    } catch {
      setQuestionData(mockQuestion.recipe);
    }

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

    let roundEvaluation = mockQuestion.output;

    try {
      const response = await fetch(`${API_BASE_URL}/sendingredients`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipe: questionData,
          input: guess,
          output: null,
        }),
      });

      if (!response.ok) {
        throw new Error('Unable to submit ingredients to server.');
      }

      const payload = await response.json();
      setQuestionData(payload.recipe || questionData);
      roundEvaluation = payload.output || mockQuestion.output;
    } catch {
      roundEvaluation = mockQuestion.output;
    }

    setEvaluation(roundEvaluation);

    const updatedRatings = [...roundRatings, normalizeRoundScore(roundEvaluation.rating)];
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

  useEffect(() => {
    localStorage.setItem(SAVED_RECIPES_KEY, JSON.stringify(savedRecipes));
  }, [savedRecipes]);

  const saveCurrentRecipe = () => {
    if (!questionData || isCurrentRecipeSaved) {
      return;
    }

    setSavedRecipes((previousRecipes) => [...previousRecipes, questionData]);
  };

  if (currentPage === 'saved') {
    return (
      <div className="app">
        <main className="card">
          <div className="header-row">
            <h1>Saved Recipes</h1>
            <button type="button" onClick={() => setCurrentPage('game')}>
              Back to Game
            </button>
          </div>

          {savedRecipes.length === 0 && <p>No saved recipes yet.</p>}

          {savedRecipes.length > 0 && (
            <div className="saved-list">
              {savedRecipes.map((recipe) => (
                <article key={recipe.id} className="saved-item">
                  <img
                    src={recipe.image_url}
                    alt={recipe.details.title}
                    className="saved-image"
                  />
                  <h3>{recipe.details.title}</h3>
                  <h4>Ingredients</h4>
                  <ul>
                    {recipe.details.ingredients.map((ingredient, index) => (
                      <li key={`${recipe.id}-ingredient-${index}`}>{ingredient}</li>
                    ))}
                  </ul>
                  <p>{recipe.details.preparation}</p>
                </article>
              ))}
            </div>
          )}
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <main className="card">
        <div className="header-row">
          <h1>Recipe Guesser</h1>
          <button type="button" onClick={() => setCurrentPage('saved')}>
            Saved Recipes ({savedRecipes.length})
          </button>
        </div>
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
            <div className="header-row">
              <h2>Evaluation</h2>
              <button type="button" onClick={saveCurrentRecipe} disabled={isCurrentRecipeSaved}>
                {isCurrentRecipeSaved ? 'Recipe Saved' : 'Save Recipe'}
              </button>
            </div>
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
