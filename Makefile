test-photpipe:
	@(cd workdir && rm *)
	@(cd workdir && ln -s /Volumes/External/NGTS/prodstore/PhotPipe_P.5006804_F.NG0522-2518_C.802_N.20160218_A.117873_S.2016_T.TEST16/*.fits .)
	(cd workdir && python $(PWD)/ngphotpipeqa.py -r P.5006804_F.NG0522-2518_C.802_N.20160218 \
		-w $(PWD)/static/PhotPipe/5006804 \
		-m QA_MANIFEST)
	@echo
	@-ls workdir/*.png
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST

test-mergepipe:
	@(cd workdir && rm *)
	@(cd workdir && ln -s /Volumes/External/NGTS/prodstore/MergePipe_P.5007803_F.NG0522-2518_C.802_S.2016_T.TEST16/*.fits .)
	(cd workdir && python $(PWD)/ngmergepipeqa.py -r P.5007803_F.NG0522-2518_C.802_S.2016_T.TEST16 \
		-w $(PWD)/static/MergePipe/5007803 \
		-m QA_MANIFEST)
	@echo
	@-ls workdir/*.png
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST

test-sysrempipe:
	@(cd workdir && rm *)
	@(cd workdir && ln -s /Volumes/External/NGTS/prodstore/SysremPipe_P.5008602_F.NG0522-2518_S.2016_T.TEST16A/*.fits .)
	(cd workdir && python $(PWD)/ngsysrempipeqa.py -r P.5008602_F.NG0522-2518_C.802_S.2016_T.TEST16A \
		-w $(PWD)/static/SysremPipe/5008602 \
		-m QA_MANIFEST)
	@echo
	@echo "\nMANIFEST:\n"
	@cat workdir/QA_MANIFEST

test-all: test-photpipe test-mergepipe test-sysrempipe
	@tree $(PWD)/static
