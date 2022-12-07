#!/usr/bin/env python

import sys, os, time, subprocess
import taxonomy as t

class _autoVivification(dict):
        """Implementation of perl's autovivification feature."""
        def __getitem__(self, item):
                try:
                        return dict.__getitem__(self, item)
                except KeyError:
                        value = self[item] = type(self)()
                        return value

if __name__ == '__main__':
        t.loadTaxonomy( sys.argv[1] if sys.argv[1] else None )
        allStr = _autoVivification()
        plevels = [ "superkingdom", "phylum", "class", "order", "family", "genus", "species", "strain" ]

        sys.stderr.write( "Parsing genome size from BWA .ann files...\n" )
        # take pangia db BWA .ann
        for line in sys.stdin:
                if '|' in line:
                        tmp = line.split(' ')
                        # skip HOST sequences
                        if '|H' in tmp[1]:
                                continue
                        else:
                                r = tmp[1].split('|')
                                tid = r[2]

                                if tid.endswith(".0"):
                                        tid = tid.split(".")[0]

                                lng = t.taxid2lineageDICT(tid, 1, 1)

                                for rank in plevels:
                                        #res_tree[pid][tid] = 1
                                        tid = lng[rank]['taxid']
        
                                        # if no particular rank for this organism, use strain
                                        if tid == 0:
                                                tid = lng[rank]['name'] # for example: 'Flaviviridae - no_o_rank - no_c_rank'

                                        if tid in allStr:
                                                allStr[tid]["raw"] += int(r[1])
                                        else:
                                                allStr[tid]["raw"] = int(r[1])

        # parsing total length from summary files
        plvl_idx = dict(zip(plevels, range(8)))
        
        for lvl in plevels:
                for filename in sys.argv[2:]:
                        if lvl in filename:
                                with open( filename ) as f:
                                        sys.stderr.write( "Parsing %s...\n"%filename )
                                        for line in f:
                                                if line.startswith("Rank"): continue
                                                (l, tid, num_of_seq, max_len, min_len, total_sig_len) = line.strip().split("\t")
                                                
                                                # unwanted taxonomy
                                                if not tid in allStr: continue

                                                if plvl_idx[l] >= plvl_idx[lvl]:
                                                        allStr[tid][lvl] = total_sig_len
                                                else:
                                                        allStr[tid][lvl] = "-"
                                f.close()

        # print uniqueless file
        for tid in allStr:
                if not "raw" in allStr[tid]:
                        sys.stderr.write("[WARNING] No raw genome length found for taxid: %s\n"%tid)

                sys.stdout.write( "%s\t%s"%(tid, allStr[tid]["raw"]) )
                for rank in plevels:
                        if rank in allStr[tid]:
                                sys.stdout.write( "\t"+allStr[tid][rank] )
                        else:
                                sys.stdout.write( "\t0" )

                sys.stdout.write("\n")
        
        sys.stderr.write( "Done.\n" )
