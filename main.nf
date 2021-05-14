#!/usr/bin/env nextflow
/*
========================================================================================
                         nf-core/scovtree
========================================================================================
 nf-core/scovtree Analysis Pipeline.
 #### Homepage / Documentation
 https://github.com/nf-core/scovtree
----------------------------------------------------------------------------------------
*/

nextflow.enable.dsl = 2

log.info Headers.nf_core(workflow, params.monochrome_logs)

def json_schema = "$projectDir/nextflow_schema.json"
if (params.help) {
    def command = "nextflow run nf-core/scovtree  -profile test,docker"
    log.info NfcoreSchema.params_help(workflow, params, json_schema, command)
    exit 0
}

if (params.validate_params) {
    NfcoreSchema.validateParameters(params, json_schema, log)
}

////////////////////////////////////////////////////
/* --         PRINT PARAMETER SUMMARY          -- */
////////////////////////////////////////////////////
log.info NfcoreSchema.params_summary_log(workflow, params, json_schema)

workflow SCOV2_TREE {

    if (params.filter_gisaid){

        include { FILTERS_GISIAD } from './workflows/filters_gisiad'

        FILTERS_GISIAD()
    }
    else {

        include { PHYLOGENETIC_ANALYSIS } from './workflows/phylogenetic_analysis'

        PHYLOGENETIC_ANALYSIS ()
    }
}

workflow {
    SCOV2_TREE()
}