process CONCAT_FASTAS {
    input:
    path(fastas)

    output:
    path("sequences.concat.fasta")

    script:
    """
    cat $fastas > sequences.concat.fasta
    """
}
