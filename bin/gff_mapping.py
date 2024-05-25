#!/usr/bin/env python

import argparse
import sys
import os.path
import glob


##### This script add the mobilome prediction to the user GFF file
##### Alejandra Escobar, EMBL-EBI
##### October 19, 2023


def mobilome_parser( mobilome_clean ):
    # Parsing the mobilome prediction
    proteins_annot, mobilome_annot, mges_dict, mob_types = {}, {}, {}, {}
    source_tools = [
        "ICEfinder",
        "IntegronFinder",
        "ISEScan",
        "PaliDIS",
        "geNomad",
        "VIRify",
        "geNomad",
        "geNomad_VIRify",
    ]
    extra_annot = [
        "viphog",
        "viphog_taxonomy",
        "mobileOG",
    ]
    
    if os.stat(mobilome_clean).st_size > 0:
        with open(mobilome_clean, "r") as input_table:
            for line in input_table:
                l_line = line.rstrip().split("\t")
                # Annotation lines have exactly 9 columns
                if len(l_line) == 9:
                    contig = l_line[0]
                    annot_source = l_line[1]
                    seq_type = l_line[2]
                    start = int(l_line[3])
                    end = int(l_line[4])
                    strand = l_line[6]
                    coordinates = (start, end)
                    if annot_source in source_tools:
                        composite_key = ( contig, start, end )
                        mob_types[composite_key] = seq_type                        
                        if contig in mobilome_annot:
                            mobilome_annot[contig].append(line.rstrip())
                            mges_dict[contig].append(coordinates)
                        else:
                            mobilome_annot[contig] = [line.rstrip()]
                            mges_dict[contig] = [coordinates]
                    else:
                        str_composite_key = (contig, str(start), str(end), strand)
                        attrib = l_line[8]
                        extra_list = []
                        for attr in attrib.split(";"):
                            att_key = attr.split("=")[0]
                            att_val = attr.split("=")[1]
                            if att_key in extra_annot:
                                extra_list.append(attr)
                        if len(extra_list) > 0:
                            extra_val = ";".join(extra_list)
                            proteins_annot[str_composite_key] = extra_val

    return (proteins_annot, mobilome_annot, mges_dict, mob_types)


# Adding the mobilome predictions to the user file
def gff_updater(user_gff, proteins_annot, mobilome_annot, mges_dict, mob_types ):
    used_contigs = []
    if os.stat(user_gff).st_size > 0:
        with open(user_gff, "r") as input_table, open("user_mobilome_extra.gff", "w") as output_extra, open("user_mobilome_full.gff", "w") as output_full, open("user_mobilome_clean.gff", "w") as output_clean:
            for line in input_table:
                l_line = line.rstrip().split("\t")
                # Annotation lines have exactly 9 columns
                if len(l_line) == 9:
                    contig = l_line[0]
                    start = l_line[3]
                    end = l_line[4]
                    strand = l_line[6]
                    composite_val = (contig, start, end, strand)
                    if not contig in used_contigs:
                        used_contigs.append(contig)
                        # Writing the mobilome entries in every output
                        if contig in mobilome_annot:
                            for mge in mobilome_annot[contig]:
                                output_clean.write(mge + "\n")
                                output_extra.write(mge + "\n")
                                output_full.write(mge + "\n")

                            # Finding mobilome proteins in the user file
                            u_prot_start = int(start)
                            u_prot_end = int(end)
                            u_prot_range = range(u_prot_start, u_prot_end + 1)
                            u_prot_len = u_prot_end - u_prot_start
                            passenger_flag = 0
                            mge_loc = []
                            for coordinates in mges_dict[contig]:
                                mge_start = coordinates[0]
                                mge_end = coordinates[1]
                                mge_range = range(mge_start, mge_end + 1)
                                mge_label = mob_types[( contig, mge_start, mge_end  )]
                                intersection = len(list(set(mge_range) & set(u_prot_range)))
                                if intersection > 0:
                                    u_prot_cov = float(intersection) / float(u_prot_len)
                                    if u_prot_cov > 0.75:
                                        passenger_flag = 1
                                        mge_loc.append(mge_label)
                            if passenger_flag == 1:
                                mge_loc = 'mge_location=' + ','.join(mge_loc)
                                if composite_val in proteins_annot:
                                    extra_annot = proteins_annot[composite_val]
                                    output_clean.write(line.rstrip() + ";" + extra_annot + ";" + mge_loc + "\n")
                                else:
                                    output_clean.write(line.rstrip() + ";" + mge_loc + "\n" )
                                        
                    if composite_val in proteins_annot:
                        extra_annot = proteins_annot[composite_val]
                        output_extra.write(line.rstrip() + ";" + extra_annot + "\n")
                        output_full.write(line.rstrip() + ";" + extra_annot + "\n")
                    else:
                        output_full.write(line.rstrip() + "\n")
                
                else:
                    output_clean.write(line.rstrip() + "\n")
                    output_extra.write(line.rstrip() + "\n")
                    output_full.write(line.rstrip() + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="This script add the extra annotations to the user GFF file"
    )
    parser.add_argument(
        "--mobilome_clean",
        type=str,
        help="Mobilome prediction on prokka gff file containing the mobilome proteins",
        required=True,
    )
    parser.add_argument(
        "--user_gff",
        type=str,
        help="User GFF file",
        required=True,
    )
    args = parser.parse_args()

    ## Calling functions
    # Storing the mobilome predictions
    ( proteins_annot, mobilome_annot, mges_dict, mob_types ) = mobilome_parser(args.mobilome_clean)

    # Adding the mobilome predictions to the user file
    gff_updater( args.user_gff, proteins_annot, mobilome_annot, mges_dict, mob_types )


if __name__ == "__main__":
    main()
