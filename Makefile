.PHONY: help install dev build up down migrate shell test clean deploy

help:
	@echo "Available commands:"
	@echo "  make install     - Install backend and frontend dependencies"
	@echo "  make dev         - Run development server (backend + frontend)"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start Docker containers"
	@echo "  make down        - Stop Docker containers"
	@echo "  make migrate     - Run Django migrations"
	@echo "  make shell       - Open Django shell"
	@echo "  make test        - Run Django tests"
	@echo "  make clean       - Clean up Docker volumes and images"
	@echo "  make deploy      - Deploy to production"

install:
	pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:5173"
	python manage.py runserver &
	cd frontend && npm run dev

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

migrate:
	python manage.py migrate

shell:
	python manage.py shell

test:
	python manage.py test

clean:
	docker-compose down -v
	docker system prune -f

deploy:
	./deploy.sh
