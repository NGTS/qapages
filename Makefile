ifneq ($(wildcard /Volumes/Extra/*),)
	DATADIR := /Volumes/Extra
else
	DATADIR := /Volumes/External
endif

test-refcatpipe:
	@(cd workdir && rm -f *)
	@(cd workdir && ln -s $(DATADIR)/NGTS/prodstore/RefCatPipe_P.5006373_F.NG0522-2518_C.802_A.110294_T.TEST15/* .)
	(cd workdir && python $(PWD)/ngrefcatpipeqa.py \
		-w $(PWD)/static/RefCatPipe/5006373 \
		-m QA_MANIFEST)
	@echo
	@-ls workdir/*.png
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST


test-photpipe:
	@(cd workdir && rm -f *)
	@(cd workdir && ln -s $(DATADIR)/NGTS/prodstore/PhotPipe_P.5006804_F.NG0522-2518_C.802_N.20160218_A.117873_S.2016_T.TEST16/*.fits .)
	(cd workdir && python $(PWD)/ngphotpipeqa.py -r P.5006804_F.NG0522-2518_C.802_N.20160218 \
		-w $(PWD)/static/PhotPipe/5006804 \
		-m QA_MANIFEST)
	@echo
	@-ls workdir/*.png
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST

test-mergepipe:
	@(cd workdir && rm *)
	@(cd workdir && ln -s $(DATADIR)/NGTS/prodstore/MergePipe_P.5007803_F.NG0522-2518_C.802_S.2016_T.TEST16/*.fits .)
	(cd workdir && python $(PWD)/ngmergepipeqa.py -r P.5007803_F.NG0522-2518_C.802_S.2016_T.TEST16 \
		-w $(PWD)/static/MergePipe/5007803 \
		-m QA_MANIFEST)
	@echo
	@-ls workdir/*.png
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST

test-sysrempipe:
	@(cd workdir && rm *)
	@(cd workdir && ln -s $(DATADIR)/NGTS/prodstore/SysremPipe_P.5008602_F.NG0522-2518_S.2016_T.TEST16A/*.fits .)
	(cd workdir && python $(PWD)/ngsysrempipeqa.py -r P.5008602_F.NG0522-2518_C.802_S.2016_T.TEST16A \
		-w $(PWD)/static/SysremPipe/5008602 \
		-m QA_MANIFEST || (echo "HAVE YOU LINKED THE DATA DIRECTORY CORRECTLY???" && false))
	@echo
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST

test-all: test-photpipe test-mergepipe test-sysrempipe test-refcatpipe
	@tree $(PWD)/static
