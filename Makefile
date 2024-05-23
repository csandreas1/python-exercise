.PHONY: run

.PHONY: url-shortener-help
url-shortener-help:
	docker compose exec python-app poetry run python url_shortener.py --help

.PHONY: minify
minify:
	docker compose exec python-app poetry run python url_shortener.py --minify $(url)

.PHONY: expand
expand:
	docker compose exec python-app poetry run python url_shortener.py --expand $(url)

