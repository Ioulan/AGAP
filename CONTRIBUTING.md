# Contributing to AGAP

:wave: Hello! Thank you for your interest in contributing to **AGAP Project**!
This guide will help you add new government agencies, improve existing entries, or update logo assets.

### 🧩 Data Structure
We keep the flashcard content in CSV files for easy editing and version control:

1.  **Main Agency Data**: `src/data/agap.csv`
    *   **guid**: Unique identifier (8-character hex). **you can leave this blank!** The reorder script generates this for you.
    *   **Acronym**: Official abbreviation (e.g., AFP, BIR).
    *   **Pronunciation**: Phonetic version for TTS (e.g., `A F P`, `Dep Ed`). **you can leave this blank!** The reorder script auto-generates this too.
    *   **FullName**: Official English/Tagalog name.
    *   **Logo**: Filename (e.g., `agap-logo-<acronym>.svg`).
    *   **Info**: Brief description or notes.
2.  **Logo Attribution**: `sources.csv`
    *   Links to Wikimedia source and licensing info for each logo.

### 🖼️ Adding a New Agency or Logo
1.  **Find the Logo**: Locate the official seal on [Wikimedia Commons](https://commons.wikimedia.org/).
    *   **💡 Pro Tip**: Use `File:ACRONYM PH site:wikimedia.org` in search (e.g., `File:DOH PH site:wikimedia.org`).
2.  **Update `src/data/agap.csv`**: Add a new row. You can leave the `guid` and `Pronunciation` empty.
3.  **Update `sources.csv`**: Add the Wikimedia `File:` URL and license info for the logos.
4.  **Finalize & Sync**: Run the following commands to download assets, generate your GUID/phonetics, and sort the data:
    ```bash
    pipenv run download
    pipenv run reorder
    ```
5.  **Build & Verify**:
    ```bash
    pipenv run build
    ```
6.  **Submit your changes**: Create a Pull Request (PR).

---

### 🛠️ Working with Brain Brew
This project uses **Brain Brew** to compile your CSVs into Anki-ready data:
*   `recipes/build_agap.yaml`: The main build instructions.
*   `src/note_models/agap.yaml`: The design and layout of the cards.
*   `src/note_models/style.css`: The global CSS styling.

---

### 🔀 Sorting & Automation
For data consistency, we keep `agap.csv` and `sources.csv` in alphabetical order, with **DDS** locked at **Row 69**.
Our utility script handles all the heavy lifting (sorting, GUID generation, and phonetic spacing):
```bash
pipenv run reorder
```
