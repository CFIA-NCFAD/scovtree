#!/usr/bin/env nextflow
/*
========================================================================================
                         nhhaidee/scovtree
========================================================================================
 nhhaidee/scovtree Analysis Pipeline.
 #### Homepage / Documentation
 https://github.com/nhhaidee/scovtree
----------------------------------------------------------------------------------------
*/

nextflow.enable.dsl = 2

log.info Headers.nf_core(workflow, params.monochrome_logs)

def json_schema = "$projectDir/nextflow_schema.json"
if (params.help) {
    def command = "nextflow run nhhaidee/scovtree -profile test,docker"
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

workflow {

    if (params.gisaid_sequences && params.gisaid_metadata){

        include { PHYLOGENETIC_GISAID } from './workflows/phylogenetic_gisaid'

        PHYLOGENETIC_GISAID()
    }
    else {

        include { PHYLOGENETIC_ANALYSIS } from './workflows/phylogenetic_analysis'

        PHYLOGENETIC_ANALYSIS ()
    }
}
