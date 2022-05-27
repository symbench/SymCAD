.PHONY: all docs

all : docs

docs :
	@mkdir -p docs
	@echo "Test Doc" > docs/index.html
