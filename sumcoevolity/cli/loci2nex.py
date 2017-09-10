#! /usr/bin/env python

"""
CLI program for converting a *.loci file from ipyrad to nexus format.
"""

import os
import sys
import argparse

import sumcoevolity

def main(argv = sys.argv):
    sumcoevolity.write_splash(sys.stderr)
    parser = argparse.ArgumentParser()

    parser.add_argument('loci_path',
            metavar = 'IPYRAD-LOCI-FILE-PATH',
            type = sumcoevolity.argparse_utils.arg_is_file,
            help = ('Path to the ipyrad loci file.'))
    parser.add_argument('-d', '--sample-to-delete',
            action = 'append',
            type = str,
            metavar = "SAMPLE-ID",
            help = ('The ID of a sequence that should not be included in the '
                    'nexus alignment. This option can be used multiple times '
                    'to remove multiple samples.'))
    parser.add_argument('-r', '--remove-triallelic-sites',
            action = 'store_true',
            help = ('By default, sites with more than two alleles are left in '
                    'the alignment, as is. When this option is specified, '
                    'these sites are removed.'))

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    data = sumcoevolity.parsing.PyradLoci(args.loci_path,
            remove_triallelic_sites = args.remove_triallelic_sites,
            sequence_ids_to_remove = args.sample_to_delete)
    seqs_removed = data.removed_sequence_counts
    sys.stderr.write("Command: {0}\n".format(" ".join(argv)))
    sys.stderr.write("\tNumber of taxa:  {0}\n".format(data.number_of_taxa))
    sys.stderr.write("\tNumber of loci:  {0}\n".format(data.number_of_loci))
    sys.stderr.write("\tNumber of sites: {0}\n".format(data.number_of_sites))
    sys.stderr.write("\tNumber of triallelic sites found:   {0}\n".format(
            data.number_of_triallelic_sites_found))
    sys.stderr.write("\tNumber of triallelic sites removed: {0}\n".format(
            data.number_of_triallelic_sites_removed))
    if seqs_removed:
        sys.stderr.write("\tNumber of sequences removed:\n")
        for n, c in seqs_removed.items():
            sys.stderr.write("\t\t{0}: {1}\n".format(n, c))
            
    data.write_nexus()

if __name__ == "__main__":
    main()
