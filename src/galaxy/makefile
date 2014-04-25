# recursive target to do install to DEST, with extra excludes EXCL.

FILE_ROOTS=fastqValidateE3 bamValidateE3 \
             bwaAlignE3 starAlignE3 tophatAlignE3 \
             hotspotE3 macsE3 \
             mergeBamsE3 bamToBigWigE3

alpha:
	${MAKE} doInstall DEST=${GEHOME} SETTINGS=settingsHgwdev.txt

install:
	${MAKE} doInstall DEST=/data/encode3/galaxy-dist/tools/encode \
	        SETTINGS=settingsEncode-01.txt

doInstall:
	@mkdir -p ${DEST}/
	for root in ${FILE_ROOTS}; do \
	    cp -p --update $${root}.py ${DEST}; \
	    cp -p --update $${root}.xml ${DEST}; \
	done
	cp -p --update ${SETTINGS} ${DEST}/settingsE3.txt

