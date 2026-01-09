clean:
	find . | grep -E "(__pycache__$|\.pyc$|\.pyo$|.idea$|.ruff_cache$)" | xargs rm -rf

dev:
	docker compose up --build --remove-orphans

format:
	uv run ruff format

lint:
	uv run ruff check --fix

push: format lint
