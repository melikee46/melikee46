# How It Works

This repository powers the profile README with a minimalist aesthetic and automated daily updates.

## Architecture & Files
- `assets/header.svg`: 1200x300 responsive SVG with light/dark theme support and breathing vermilion seal.
- `assets/divider.svg`: Hairline separator with vermilion center dot.
- `data/movements.json`: Curated art movements with period, description, and key artist.
- `scripts/update_readme.py`: Idempotent script selecting today's movement and fetching recent public repos.
- `.github/workflows/update.yml`: Scheduled GitHub Actions workflow updating `README.md` daily at midnight.
- `README.md`: Profile template with `<!--MOVEMENT:...-->` and `<!--REPOS:...-->` injection markers.

## Adding an Art Movement
To add a movement, append an entry to `data/movements.json`:
```json
{
  "name": "De Stijl",
  "period": "1917 – 1931",
  "description": "Reduced visual form to primary colors and geometric verticals/horizontals.",
  "artist": "Piet Mondrian"
}
```
The script deterministically picks the movement using `(day_of_year - 1) % len(movements)`.
