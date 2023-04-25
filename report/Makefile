all: report.pdf

report.pdf: report.tex font.tex layout.tex title.tex 
	mkdir -p build
	pdflatex -synctex=1 -interaction=batchmode -output-directory=build report.tex 

diagrams/price-curve.pdf: diagrams/price-curve.drawio
	drawio -x --crop -o diagrams/price-curve.pdf diagrams/price-curve.drawio
	
diagrams/cow2.pdf: diagrams/cow2.drawio
	drawio -x --crop -o diagrams/cow2.pdf diagrams/cow2.drawio
	
diagrams/sub-merged.pdf: diagrams/sub-merged.drawio
	drawio -x --crop -o diagrams/sub-merged.pdf diagrams/sub-merged.drawio
	
diagrams/wrapper.pdf: diagrams/wrapper.drawio
	drawio -x --crop -o diagrams/wrapper.pdf diagrams/wrapper.drawio

diagrams/%.eps: ../quantitative_results/data_analysis.ipynb
	jupyter nbconvert --execute $< --to notebook --output tmp
	rm tmp.ipynb

drawio-diagrams: diagrams/wrapper.pdf diagrams/sub-merged.pdf diagrams/cow2.pdf diagrams/price-curve.pdf

notebook-diagrams: diagrams/*.eps

diagrams: *.pdf *.eps
