pip: # install pip libraries
	@pip install -r requirements.txt

test:
	coverage run --source=. -m unittest discover -s tests/ -p '*.py'

report : test
	coverage html

run_bot_listener: 
	@python -m src.services.listener_bot

run_error_api: 
	@python -m src.services.errors_from_api

run_error_tasks: 
	@python -m src.services.errors_from_tasks

deploy_tsuru:
	tsuru app deploy . --app slack-bot-dbaas-error-gcp

tsuru_shell:
	tsuru app shell --app slack-bot-dbaas-error-gcp -i