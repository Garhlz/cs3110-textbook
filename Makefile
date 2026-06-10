# REMOTE is the name of the git remote that hosts
# https://github.com/cs3110/textbook. The gh-pages branch there is
# automatically served by https://cs3110.github.io/textbook.
REMOTE=origin

BOOK=src
HTML=${BOOK}/_build/html
LATEX=${BOOK}/_build/latex
PDF_NAME=ocaml_programming.pdf
UV_JB=.venv/bin/jupyter-book
UV_GHP=.venv/bin/ghp-import
BOOK_ZH=zh-cn
HTML_ZH=${BOOK_ZH}/_build/html

default: html

clean:
	jupyter-book clean ${BOOK}

clean-uv:
	${UV_JB} clean ${BOOK}

clean-zh:
	jupyter-book clean ${BOOK_ZH}

clean-zh-uv:
	${UV_JB} clean ${BOOK_ZH}

html:
	OPAMSWITCH=textbook jupyter-book build ${BOOK}

html-uv:
	OPAMSWITCH=textbook ${UV_JB} build ${BOOK}

html-zh:
	OPAMSWITCH=textbook jupyter-book build ${BOOK_ZH}

html-zh-uv:
	OPAMSWITCH=textbook ${UV_JB} build ${BOOK_ZH}

html-strict:
	jupyter-book build -W ${BOOK}

linkcheck:
	jupyter-book build ${BOOK} --builder linkcheck

view:
	open ${HTML}/index.html

localserver:
	python -m http.server --directory src/_build/html 8080

viewlocalserver:
	open http://localhost:8080

pdf:
	jupyter-book build src --builder pdflatex

view-pdf:
	open ${LATEX}/book.pdf

deploy: html pdf
	cp ${LATEX}/book.pdf ${HTML}/${PDF_NAME} \
	  && ghp-import -n -p -f ${HTML} -r ${REMOTE} -m "Update textbook"

deploy-zh: html-zh
	ghp-import -n -p -f ${HTML_ZH} -r ${REMOTE} -m "Deploy Chinese edition"

deploy-zh-uv: html-zh-uv
	${UV_GHP} -n -p -f ${HTML_ZH} -r ${REMOTE} -m "Deploy Chinese edition"

wc:
	find src/chapters -type f -name "*.md" -exec cat {} \; | pandoc -f commonmark -t plain | wc -w

wcl:
	find -E src/chapters -type f -name "*.md" -exec pandoc --lua-filter wordcount.lua {} \; | awk '{s+=$$1} END {print s}'

ccl:
	find -E src/chapters -type f -name "*.md" -exec pandoc --lua-filter codecount.lua {} \; | awk '{s+=$$1} END {print s}'
