# installs scripts to tools directory

STEP_SCRIPTS=eap_run_bwa_pe eap_run_bwa_se eap_run_slx_bwa_pe eap_run_slx_bwa_se \
             eap_run_rsem_long_pe eap_run_rsem_long_se \
             eap_run_star_long_pe eap_run_star_long_se \
             eap_run_tophat_long_pe eap_run_tophat_long_se \
	     eap_run_bam_to_bw_all_minus eap_run_bam_to_bw_all_plus \
	     eap_run_bam_to_bw_uniq_minus eap_run_bam_to_bw_uniq_plus \
             eap_run_hotspot eap_run_phantom_peak_spp eap_run_spp_chip_se \
             eap_run_macs2_chip_pe eap_run_macs2_chip_se \
             eap_run_macs2_dnase_pe eap_run_macs2_dnase_se
MORE_SCRIPTS=eap_bam_sort eap_broadPeak_to_bigBed eap_dnase_stats eap_eval_bam \
             eap_macs2_xls_to_narrowPeak eap_narrowPeak_to_bigBed eap_pool_big_wig \
             eap_pool_hotspot eap_sum_bigWig

# NOTE: tools.ra is actively changing in /hive/groups/encode/encode3/tools and 
#       SHOULD NOT be copied from the repository to that location at this time.
#       Instead, copy that version to your repository and keep the repository up to date.

ALL_FILES=${STEP_SCRIPTS} ${MORE_SCRIPTS}

alpha:
	${MAKE} doInstall TOOLS_DIR=${EAP_TOOLS_DIR}

install:
	${MAKE} doInstall  TOOLS_DIR=/hive/groups/encode/encode3/tools/

doInstall:
	@mkdir -p ${TOOLS_DIR}/
	for file in ${ALL_FILES}; do \
	    cp -p --update $$file ${TOOLS_DIR}; \
	done

