build:
		docker-compose build

up:
		docker-compose up -d

down:
		docker-compose down


test:
		python3 manage.py test --pattern="tests*.py"