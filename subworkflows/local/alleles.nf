
params.options    = [:]
include { DETERMINE_SNPS } from '../../modules/local/determine_snps'  addParams( options: params.options    )

workflow ALLELES {
    take:
    fasta

    main:
    DETERMINE_SNPS (fasta)

    emit:
    alleles = DETERMINE_SNPS.out.alleles

}