all: serve

build:
	docker build -t flask-api .

serve: build
	docker run -ti -p 1337:1337 --rm --name test-api flask-api

test.csv:
	@echo "======================="
	@echo "Testing example payload"
	@echo "======================="
	@echo " "
	./scripts/post.sh data/test.json > test.csv
	@echo "File saved to test.csv"

blank.csv:
	@echo "====================================="
	@echo "Testing defaults/empty field handling"
	@echo "====================================="
	@echo " "
	./scripts/post.sh data/blank.json > blank.csv
	@echo "Files saved to blank.csv"

ping:
	curl -v http://localhost:1337/ping

clean:
	rm -rf test.csv
	rm -rf blank.csv

.PHONY: test.csv blank.csv
test: test.csv
blank: blank.csv
