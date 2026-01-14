# 📸 GMap Screenshot Engine

> A powerful, automated engine to capture high-quality screenshots from Google Maps using Scrapy and Playwright. Designed for scale and efficiency.

## ✨ Features

- 🕷️ **Scrapy & Playwright**: Robust crawling with full browser rendering for accurate screenshots.
- 🎯 **Dynamic Targeting**: Fetches target locations directly from a **Postgres** database.
- ☁️ **Cloud Storage**: Automatically compresses and uploads processed images to **AWS S3**.
- 🐳 **Docker Native**: Fully containerized environment for easy deployment and development.
- 🧹 **Clean & Maintainable**: Styled with `ruff` for consistent code quality.

## 🛠️ Tech Stack

- **Core**: Python 3.12, Scrapy, Playwright
- **Data**: PostgreSQL, Redis
- **Infrastructure**: Docker, Docker Compose
- **Storage**: AWS S3

## 🚀 Getting Started

### 1. Environment Setup

Clone the repository and configure your environment variables:

```bash
cp .example.env .env
```

Edit the `.env` file with your credentials (Postgres, AWS S3).

### 2. Run the Engine

Start the application and all services using Docker Compose:

```bash
make dev
```

This command builds the images and starts the containers in the foreground.

### 3. Development Commands

Useful shortcuts defined in the `Makefile`:

- `make format` - Format code using `ruff`.
- `make lint` - Check code quality and fix issues.
- `make push` - Run format and lint checks before pushing.
- `make clean` - Remove cache and temporary files.

---

<p align="center">
  <sub>Made with ❤️ for Open Source</sub>
</p>
