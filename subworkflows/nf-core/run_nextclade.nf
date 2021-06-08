
params.options    = [:]
include { NEXTCLADE } from '../../modules/nf-core/software/nextclade/main'  addParams( options: params.options    )

workflow RUN_NEXTCLADE {
    take:
    ch_fasta
    output_format

    main:
    NEXTCLADE (ch_fasta, output_format)

    emit:
    nextclade_metadata  = NEXTCLADE.out.csv
}