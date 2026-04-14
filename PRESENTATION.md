# Project Presentation Tips

This file contains a short slide outline and speaker notes for a **3-minute presentation** of the project.

## Goal

Present the project quickly and clearly:

- what the idea is
- which data we use
- how the technical flow works
- what makes the trivia original
- what could be added in the future

## Suggested Slide Structure

### Slide 1. Title and idea

**Title:**
Recipe Trivia from Open Data Hub

**Key message:**
This is not a classic trivia quiz.  
The user sees only a recipe photo and has to guess the ingredients.

**What to say:**
We wanted to build a trivia experience that is more visual and interactive than usual quizzes. Instead of answering general knowledge questions, the user has to understand a dish from its image and guess its ingredients.

### Slide 2. Data source

**Title:**
Starting from Open Data Hub data

**Key message:**
The project uses recipe data taken from Open Data Hub.

**What to say:**
We decided to start from real structured data. We take a random recipe from the available Open Data Hub recipe dataset. From that data we get the image, the recipe title, and especially the official list of ingredients.

### Slide 3. Technical flow

**Title:**
How the workflow works

**Suggested flow on slide:**
1. Get a random recipe from Open Data Hub
2. Show only the recipe image to the user
3. The user writes the guessed ingredients
4. Send the JSON payload to Together AI
5. Receive structured feedback in JSON

**What to say:**
After selecting a random recipe, we show only the image. The user writes the ingredients they think are in the recipe. Then we send a JSON payload containing the real recipe ingredients and the user answer to Together AI. We use Together AI to test the API and process the JSON response in a structured way.

### Slide 4. What the LLM returns

**Title:**
How the LLM is used

**Key message:**
The model does not invent a new recipe. It compares user input with the correct ingredients.

**What to say:**
The LLM checks whether the guessed ingredients are correct or not, ingredient by ingredient. It returns a rating, a simple explanation, and a mapping between correct ingredients and proposed ones. This makes the response easy to use in the backend and easy to show in the frontend.

### Slide 5. Game logic

**Title:**
Trivia gameplay

**Key message:**
The user plays 5 rounds and gets a final score.

**What to say:**
The user has to respond to 5 different recipes. After each recipe, they receive feedback about which ingredients were correct and a short explanation. At the end of the 5 tries, the system computes a final score.

### Slide 6. Future improvements

**Title:**
Future ideas

**What to say:**
We already identified some possible extensions:

1. A scoreboard, to make the game more competitive and replayable.
2. A reward system connected to local restaurants, for example a discount on a restaurant from Open Data Hub if the user gets enough points.

## Very Short Talk Track

If you need an even shorter version for 3 minutes:

**Problem / idea**
We wanted to create a trivia experience that is different from the usual question-and-answer format.

**Data**
We use recipe data from Open Data Hub and randomly select one recipe at a time.

**Interaction**
The user sees only the recipe photo and tries to guess the ingredients.

**AI usage**
We send the recipe data and the user answer as JSON to Together AI, which returns a structured evaluation.

**Game**
The user plays 5 rounds, gets feedback after each round, and receives a final score at the end.

**Future**
Possible next steps are a scoreboard and rewards such as a restaurant discount.

## Tips for the slides

- Keep slides visual and light on text.
- Show the flow as a simple pipeline.
- Use one concrete recipe example to make the idea immediate.
- Emphasize that the project combines **real data + AI evaluation + game interaction**.
- Avoid too much technical detail in the spoken presentation.
- Focus on what makes the idea original: guessing ingredients from a photo.

## One-Sentence Summary

Our project turns Open Data Hub recipe data into a visual trivia game where users guess ingredients from recipe photos, receive AI-based feedback through Together AI, and get a final score after 5 rounds.
