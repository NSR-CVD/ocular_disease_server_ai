dev-local:
		@echo Start service for developer
		docker-compose -f local.yml up -d
		docker exec -it health-me-server-ai sh

clean-local:
		@echo Start service for developer
		docker-compose -f local.yml down