# How It Works

This repository powers Melike's GitHub profile README with a cozy, fairy-like aesthetic and automated daily workflows.

## Architecture & Assets
- `assets/banner.png`: 1200x400 original pixel-art banner of a cozy night desk with code, plants, and fairy lights.
- `data/movements.json`: Curated art movements (period, description, key artist).
- `scripts/update_readme.py`: Idempotent script selecting today's movement and fetching recent public repositories.
- `.github/workflows/update.yml`: Scheduled workflow updating `README.md` daily at midnight UTC.
- `.github/workflows/snake.yml`: Generates contribution snake SVGs and publishes them to the `output` branch.
- `README.md`: Profile template containing dynamic `<!--MOVEMENT:...-->` and `<!--REPOS:...-->` injection markers.

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
The update script deterministically picks the movement via `(day_of_year - 1) % len(movements)`.
