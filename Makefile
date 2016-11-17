all:
	sh ~/bob/run.sh

clean_pyc:
	find -name '*.pyc' -delete

manual: instrukcja.tex
	texi2pdf instrukcja.tex

clean: clean_pyc
	rm instrukcja.aux instrukcja.log instrukcja.toc __pycache__ -rf

zip: manual clean
	cp . /tmp/bob -r
	rm /tmp/bob/img -rf
	rm /tmp/bob/tags
	zip -r bob.zip /tmp/bob
	
