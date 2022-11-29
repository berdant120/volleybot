.PHONY: all test build run git-update

all: git-update test build run

git-update:
	git pull
test:
	@echo "Running tests.."
	PYTHONPATH=src python3 -m pytest test
build:
	@echo "Running build.."
	docker-compose build
run:
	docker-compose run telegram_bot_app
