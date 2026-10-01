---
name: Nome in codice
description: An Italian team word game presented as a legible operational table.
colors:
  paper: "#f1eee5"
  surface: "#faf8f2"
  ink: "#222c25"
  muted: "#596154"
  line: "#c9cbbd"
  olive: "#52613b"
  team-red: "#a93f36"
  team-blue: "#34658a"
  team-ochre: "#8a681d"
  team-violet: "#67508e"
  team-green: "#347268"
  civilian: "#dedfd3"
  focus: "#8a681d"
typography:
  display:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "clamp(3.6rem, 5vw, 5rem)"
    fontWeight: 600
    lineHeight: 0.99
    letterSpacing: "-0.025em"
  heading:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "1.85rem"
    fontWeight: 600
    lineHeight: 1.1
  card-word:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "clamp(1.25rem, 2.25vw, 2.65rem)"
    fontWeight: 600
    lineHeight: 1
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "0.8rem"
    fontWeight: 600
rounded:
  control: "5px"
  card: "7px"
  panel: "10px"
  dialog: "12px"
spacing:
  board-gap: "10px"
  control-padding: "12px 18px"
  dialog-padding: "28px"
components:
  button-primary:
    backgroundColor: "{colors.olive}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "{spacing.control-padding}"
    height: "44px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "{spacing.control-padding}"
    height: "44px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
    height: "44px"
  word-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.card-word}"
    rounded: "{rounded.card}"
    padding: "10px 13px"
---

# Design System: Nome in codice

## Overview

**Creative North Star: "The Operational Table"**

The interface reads as an ivory working surface for a game run in the same room. It favors rules, compact controls, numbered positions, and clearly named team ownership over decorative espionage imagery. The board is the visual center in play; setup keeps configuration and its live allocation preview in view together.

The public board must remain readable when projected, while the Spymaster map uses the same card geometry on a phone. Functional labels carry status alongside color. Card revelation is the expressive moment: a brief tilt gives way to a persistent ownership label, strike, and check. Reduced motion removes the animation.

**Key Characteristics:**
- Warm paper and light card surfaces with dark green ink.
- Olive actions and five named team colors.
- Condensed, large game words paired with quiet sans-serif controls.
- Flat rules and outlines, with depth reserved for floating layers.

## Colors

Olive is the action accent on a restrained paper palette. Team hues encode game ownership and always appear with a team name or letter.

### Primary
- **Table Olive:** Primary actions, interactive hover borders, connection state, and supporting emphasis.

### Secondary
- **Team Red, Blue, Ochre, Violet, and Green:** Fixed selectable identities for two to five teams. The selected hue fills a team badge or known card; labels preserve identity beyond color.

### Neutral
- **Paper:** Page background.
- **Light Surface:** Inputs, covered word cards, panels, and dialogs.
- **Ink:** Main text, assassin cards, and selected segmented controls.
- **Muted Ink:** Supporting copy, card indices, and status detail.
- **Rule:** Dividers, control borders, and score outlines.
- **Civilian:** Light neutral ownership on the preview and revealed board.

**The Named Ownership Rule.** Never communicate a card's owner or active team by hue alone; show the name, letter, or status text with it.

## Typography

**Display Font:** Self-hosted Barlow Condensed, with sans-serif fallback.

**Body Font:** Self-hosted DM Sans, with sans-serif fallback.

**Character:** Condensed headings and card words make the board legible at room scale. DM Sans keeps controls and guidance calm and direct.

### Hierarchy
- **Display:** Large condensed headings; the setup heading uses a smaller responsive variant than the global heading.
- **Heading:** Condensed section and dialog titles.
- **Card word:** Centered condensed nouns that scale with the projected board. Below 760px, short words fit on one line by responding to card width and word length; longer words use natural Italian hyphenation at a readable size.
- **Body:** DM Sans for explanation and instructions.
- **Label:** Compact, semibold DM Sans for forms, statuses, and card metadata; some metadata is uppercase with modest tracking.

**The Word First Rule.** On the board, the noun receives the strongest type treatment; index and ownership remain visible but secondary.

## Layout

Setup uses a centered container up to 1328px, with a two-column form and live preview separated by a 64px gap. Below 760px the columns stack, with configuration first. The game container grows to 1800px and lets the board dominate. Both preview and live board use five equal columns; the live board can have five or six rows. The board gap tightens from 10px to 5px on narrow screens. Short card nouns scale to fit one line; longer nouns may hyphenate in Italian. Score tiles wrap on mobile, and game actions reflow beneath the board. At projection widths, card height responds to viewport height so all rows remain visible.

## Elevation & Depth

The table is flat at rest. Borders, dividers, and filled ownership cards provide structure. Floating join content and modal dialogs alone use ambient shadows; the dialog backdrop darkens the board during a deliberate decision.

### Shadow Vocabulary
- **Join popover:** `0 12px 40px #222c2526` for the open game-code form.
- **Modal dialog:** `0 18px 60px #15201840` for reveal, turn, and rules decisions.

**The Flat Table Rule.** Keep board cards and score tiles free of resting shadows; use outlines and fills to express their state.

## Shapes

Controls use gently squared corners (5px), word cards use a slightly softer edge (7px), and larger floating surfaces use 10–12px. Thin rules organize sections. A small rotation on the setup preview suggests physical cards, while the live board stays aligned in a strict grid.

## Components

### Buttons
- **Primary:** Olive fill, white text, 5px corners, semibold DM Sans, and a 44px minimum touch height. The setup action expands to 58px.
- **Secondary:** Transparent surface with a thin rule border; quiet navigation removes the border.
- **States:** Hover subtly darkens; keyboard focus gets a 3px ochre outline offset by 4px. Disabled controls reduce opacity.

### Inputs / Fields
- **Style:** Light surface, thin rule border, 5px corners, and at least 44px height. Labels sit above fields; number fields use tabular numerals.
- **Focus:** The same visible ochre outline as buttons.

### Navigation
- **Style:** A compact branded masthead with a shield symbol, room for the game code, and quiet text actions. On phones, game actions wrap onto a ruled second line.

### Score Tiles
- **Style:** Thin ruled containers show a colored letter badge, team name, status text, and remaining count. The active tile gains its team-colored inset outline; eliminated teams lose emphasis and strike through their name.

### Word Cards
- **Style:** Five-column light cards present a large centered noun and small index. Known cards show an ownership line and fill with their owner's color; civilian cards return to a light neutral. On narrow public boards, the redundant hidden-identity line disappears while revealed ownership remains visible. A reveal crosses the noun and adds a check.
- **Behavior:** Selectable covered cards gain an olive border and light olive background on hover. Reveals animate for 0.45s; reduced-motion settings remove the animation.

### AI Suggestions
- **Style:** A compact ruled surface beneath the board holds the secondary action and a short status. Suggested covered cards gain an olive border, pale olive fill, and an explicit “AI” marker; they remain distinct from revealed team identities.
- **Behavior:** Highlights appear only on request, can be hidden without repeating inference, and disappear when the clue or covered-card set changes. Copy presents them as tentative suggestions, never as revealed identities.

### Dialogs
- **Style:** Light 12px surface over a darkened backdrop, with large condensed decision text and distinct cancel and confirm actions. Reveal and turn actions require explicit confirmation.

## Do's and Don'ts

### Do:
- **Do** keep word cards in five aligned columns on public and Spymaster boards.
- **Do** pair team colors with visible names, letters, and status text.
- **Do** preserve the 44px minimum for interactive controls and the visible keyboard focus outline.
- **Do** provide a reduced-motion path for card revelation.

### Don't:
- **Don't** put resting shadows on word cards or score tiles.
- **Don't** replace the operational table with decorative spy graphics or fake telemetry.
- **Don't** make ownership, turn, or elimination status depend on color alone.
