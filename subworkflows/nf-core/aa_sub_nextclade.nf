params.options    = [:]
include { NEXTCLADE_AASUB } from '../../modules/local/aa_sub_nextclade'  addParams( options: params.options    )

workflow AASUB_NEXTCLADE{

    take:
    ch_metadata

    main:
    NEXTCLADE_AASUB (ch_metadata)

    emit:
    metada           = NEXTCLADE_AASUB.out.tsv
}