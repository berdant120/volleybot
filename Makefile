.PHONY: all test build run git-update stop

all: git-update test build stop run

git-update:
	git pull
test:
	@echo "Running tests.."
	PYTHONPATH=src python3 -m pytest test
build:
	@echo "Running build.."
	docker-compose build
stop:
	docker-compose down
run:
	docker-compose run telegram_bot_app
