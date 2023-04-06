#!/usr/bin/env python

from Bio import SeqIO
import argparse
import sys
import os.path
import glob


##### This script filters out non-mobilome annotation from momo+viri gff file and generates the outputs with three levels of information: mobilome+associated CDSs, mobilome+viphogs/mobileOG only (for MGnify), mobilome only.
##### Alejandra Escobar, EMBL-EBI
##### Feb 13, 2023


def minimal(annot):
    ### Parsing the gff file
    mge_coord = {}
    mge_id = {}
    mge_desc = {}
    mges = [
        "insertion_sequence",
        "integron",
        "conjugative_transposon",
        "plasmid",
        "viral_sequence",
        "prophage",
    ]
    flank = ["terminal_inverted_repeat_element", "attC_site", "direct_repeat"]
    valid_attr = ["viphog", "viphog_taxonomy", "mobileOG"]
    if os.path.isfile(annot):
        with (
            open(annot, "r") as input_file,
            open("mobilome_clean.gff", "w") as to_clean_gff,
            open("mobilome_extra.gff", "w") as to_extra_gff,
            open("mobilome_nogenes.gff", "w") as to_nogenes_gff
        ):
            for line in input_file:
                l_line = line.rstrip().split("\t")
                # Annotation lines have exactly 9 columns
                if len(l_line) == 9:
                    (
                        contig,
                        seq_source,
                        seq_type,
                        start,
                        end,
                        score,
                        strand,
                        phase,
                        attr,
                    ) = line.rstrip().split("\t")
                    if seq_type in flank:
                        to_clean_gff.write(line)
                        to_extra_gff.write(line)
                        to_nogenes_gff.write(line)
                    elif seq_type in mges:
                        to_clean_gff.write(line)
                        to_extra_gff.write(line)
                        to_nogenes_gff.write(line)
                    else:
                        if "from_mge" in attr:
                            to_clean_gff.write(line)
                            if any(["viphog=" in attr, "mobileOG=mobileOG" in attr]):
                                att_l = attr.split(";")
                                new_attr = [att_l[0]]
                                for element in att_l:
                                    element_key = element.split("=")[0]
                                    if element_key in valid_attr:
                                        new_attr.append(element)
                                new_attr = ";".join(new_attr)
                                to_extra_gff.write(
                                    "\t".join(
                                        [ contig,
                                            seq_source,
                                            seq_type,
                                            start,
                                            end,
                                            score,
                                            strand,
                                            phase,
                                            new_attr,
                                        ]
                                    ) + "\n"
                                )

                elif all([line.startswith("#"), not "##FASTA" in line]):
                    to_clean_gff.write(line)
                    to_extra_gff.write(line)
                    to_nogenes_gff.write(line)


def main():
    parser = argparse.ArgumentParser(
        description="This script filters out non-mobilome annotation from momo+viri gff file and generates the outputs with three levels of information: mobilome+associated CDSs (mobilome_clean.gff), mobilome+viphogs/mobileOG only (mobilome_extra.gff), mobilome only (mobilome_nogenes.gff). Please provide the gff file generated by cross_momo_viri.py script"
    )
    parser.add_argument(
        "--momoviri",
        type=str,
        help="Mobilome annotation file (gff)",
        required=True,
    )
    args = parser.parse_args()

    ### Setting up variables
    annot = args.momoviri
    minimal(annot)


if __name__ == "__main__":
    main()

