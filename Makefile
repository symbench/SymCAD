.PHONY: all docs

all : docs

docs :
	pdoc --docformat numpy --logo "https://symbench.github.io/SymCAD/images/SymCAD.png" --favicon "https://avatars.githubusercontent.com/u/70644802?s=200&v=4" -o ./docs src/symcad
