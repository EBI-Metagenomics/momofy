#!/usr/bin/env nextflow
nextflow.enable.dsl=2

process gbk_split {
    publishDir "$launchDir/icefinder_results/gbk", pattern: '*.gbk', mode: 'copy'
    publishDir "$launchDir/icefinder_results/", pattern: 'input.list', mode: 'copy'

    memory "4 GB"
    cpus 1

    input:
      path gbk_file, name: 'prokka.gbk'
      
    output:
      path "*.gbk"
      path "input.list" , emit: gbks

    tmpDir = file("$launchDir/icefinder_results/tmp")
    tmpDir.mkdirs()

    resDir = file("$launchDir/icefinder_results/result")
    resDir.mkdirs()

    script:
    if (gbk_file.size() > 0)
        """    
        gbk_splitter.pl prokka.gbk
        """
    else
        """
        echo 'ICEfinder dir empty due to empty input... generating dummy files'
        touch input.list
        touch dummy.gbk
        """

}

