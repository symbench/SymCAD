.PHONY: all docs wheel clean

all : docs

clean :
	rm -rf dist docs/symcad docs/*.html docs/*.js

docs :
	pdoc --docformat numpy --logo "https://symbench.github.io/SymCAD/images/SymCAD.png" --favicon "https://avatars.githubusercontent.com/u/70644802?s=200&v=4" -o ./docs src/symcad

wheel :
	python -m pip install build
	python -m build --wheel
	rm -rf build
