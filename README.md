# Welcome to the Open Data Hub Bootcamp 2026!

This repo will guide you through the AI/LLM data integration challenge, in which you will create a trivia game powered by Open Data Hub data and an LLM.

The goal of this bootcamp is to foster our community around the Open Data Hub, to get to know each other, the technology, but also for you to just learn stuff and make friends. This is not a competition, so don't be afraid to make mistakes and try out new stuff. Our Open Data Hub team is there to help and support you.

You will also have an opportunity to present the results to the public at our upcoming event, the Open Data Hub Day.

## The Challenge

Your goal is to build a **trivia game** that uses real data from the Open Data Hub APIs and an **LLM to generate questions** from that data.

You are free to choose **any dataset** available on the Open Data Hub — tourism POIs, mobility data, weather, events, and more. Pick something that makes for a fun game!

### How it works

The core idea is: **the Open Data Hub provides the facts, the LLM turns them into a game.**

1. **Fetch data** — call the Open Data Hub API to retrieve a random item from your chosen dataset (e.g., a random mountain hut, a random lake, a random event...).
2. **Generate the question** — send the item's data to the LLM and ask it to produce a trivia question with answer options based on those facts. The LLM's job is to transform raw API data into engaging game content.
3. **Display and play** — show the question in a web interface and let the player answer.

#### Example

Say you pick the Tourism API's POI dataset:

1. Your backend fetches a random POI — e.g., *"Lago di Braies"* with its altitude, location, description.
2. You send that data to the LLM with a prompt like: *"Generate a multiple-choice trivia question about this place based on the following data."*
3. The LLM returns: *"At what altitude does this famous Dolomite lake sit? A) 842m B) 1,496m C) 2,103m D) 1,211m"*
4. Your frontend shows the question and the player picks an answer.

### Requirements

1. **Choose a dataset** from the Open Data Hub that you find interesting.
2. **Fetch data from the APIs** — pick a random item, select the relevant fields, and clean up the data.
3. **Generate questions with the LLM** — send the data to the LLM with a prompt that tells it what kind of question to produce.
4. **Build a simple web interface** that displays the question and handles the player's answer.

### Extras

Once the base game works, pick one or more of these to make it better:

- **Free-text answers** — instead of multiple choice, let the player type their answer. Use the LLM to judge if the answer is correct (handles synonyms, partial answers, different languages — e.g., "Braies Lake" vs "Lago di Braies").
- **Adaptive difficulty** — the LLM adjusts question difficulty based on player performance (harder questions for good players, easier ones after wrong answers).
- **Multi-dataset mashup** — combine data from multiple APIs into a single question (e.g., *"Which of these ski areas is closest to a public e-charging station?"*), requiring your backend to orchestrate multiple API calls.
- **Daily challenge** — use the date as a seed so all players get the same question each day, with a shareable score.

## Datasets

You are **not limited** to any specific dataset. Use the **[Discovery tool](https://discovery.opendatahub.com/)** to browse and find datasets that inspire your game idea.

Once you've picked a dataset, refer to the relevant API documentation:

- [Tourism API](https://tourism.opendatahub.com/swagger/index.html) — POIs, activities, events, gastronomy, accommodation, ...
- [Mobility API](https://swagger.opendatahub.com/?url=https://mobility.api.opendatahub.com/v2/apispec) — traffic, sensors, parking, e-charging stations, ...

You can also use the [DataBrowser](https://databrowser.opendatahub.com/) to visually inspect the data before diving into the API.

## Hints

Since LLMs have limited input length, retrieve only the fields you need using the `fields` parameter.

Start easy — support only one language first (e.g., English), then expand.

Think about what makes a good question: your game is only as fun as the data you feed into the LLM. Pick fields that contain interesting, distinguishable facts.

## Quickstart

### 1. Fetch data from the Open Data Hub

Pick a dataset and call the API. For example, to get a random POI from the Tourism API:

```bash
curl "https://tourism.opendatahub.com/v1/ODHActivityPoi?pagenumber=1&pagesize=1&seed=42&fields=Detail.en.Title,Detail.en.BaseText,GpsInfo,AltitudeDifference"
```

This returns structured data like a place name, description, coordinates, and altitude.

### 2. Send the data to the LLM to generate a question

Take the data you fetched and include it in your prompt to the LLM:

```bash
curl -X POST "https://api.together.xyz/v1/chat/completions" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "messages": [{"role": "user", "content": "Based on the following data, generate a multiple-choice trivia question with 4 options. Mark the correct answer.\n\nData: {\"Title\": \"Lago di Braies\", \"Altitude\": 1496, \"Region\": \"Puster Valley\", \"BaseText\": \"A natural lake at the foot of the Croda del Becco...\"}"}]
  }'
```

The key point: **don't ask the LLM to invent facts** — feed it real data from the API and let it turn that data into a question.
