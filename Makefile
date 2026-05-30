.PHONY: all postpro poster clean

all: poster

postpro:
	python3 postpro/process_nbn.py

poster: postpro
	typst compile --root . poster/poster.typ poster/poster.pdf

clean:
	$(RM) plot/*.pdf plot/*.png poster/poster.pdf
