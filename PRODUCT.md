# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

SvelteKit frontend, Python FastAPI backend, Cloudflare Workers hosting and shared Cloudflare D1 database. Prefer uv for Python tooling. Cloudflare replaces the original Docker/Vercel deployment requirement; Docker is not required for cloud deployment.

## Users

An organizer running a group activity with adolescents in the same room. A projected public board and a separate mobile Spymaster view are the primary devices.

## Product Purpose

An Italian word-association team game inspired by Nome in Codice, adapted for large groups with up to five teams.

## Operating Context

Configure teams, names and colors, board size and card counts; create a game with a short URL identifier; reopen it from another device. Public and Spymaster views must share authoritative state.

## Capabilities and Constraints

- Up to five teams, boards of 25 or 30 cards.
- Configurable team, civilian and assassin counts; zero civilians permitted; enforce board capacity.
- At least 500 suitable Italian nouns seeded in the database.
- Explicit reveal confirmation and animation, scores and turn management.
- Assassin eliminates the revealing team; others continue.
- Spymaster sees assignments. An optional code protects this view; when left blank, the view opens without a login. Never include unrevealed assignments in public board API responses.
- After a clue is entered, the public board may request optional AI association suggestions for the covered words. Suggestions are local to the requesting browser, do not reveal assignments, and never make a move automatically.
- Losing games after a deployment restart was acceptable, but shared state during play is required. D1 provides durable shared storage.
- Open rule details: handling eliminated-team cards, starting-team advantage, and clue entry. Document implementation assumptions clearly.

## Brand Commitments

Il nome del prodotto è **Nome in codice**. Italian interface; espionage atmosphere reminiscent of the board game. Legibility for a projected board and a mobile Spymaster takes priority.

## Evidence on Hand

PROGETTO.md and confirmed conversation choices. No preexisting implementation or visual assets.

## Product Principles

- One authoritative game across devices.
- Clear turns and deliberate reveals.
- Readable words and team identities, also without relying solely on color.
- Fast setup for a room full of players.
