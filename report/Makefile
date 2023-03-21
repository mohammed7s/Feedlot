all: report.pdf

report.pdf: report.tex font.tex layout.tex title.tex 
	mkdir -p build
	pdflatex -synctex=1 -interaction=batchmode -output-directory=build report.tex 
