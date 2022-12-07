#!/usr/bin/env python

import sys, os, time
import taxonomy as t

def parseHeader( line ):
        line = line.strip().lstrip('>')
        temp = line.split(' ')
        name = temp[0]

        (acc,start,end,taxid,null) = name.split('|')

        return (acc,start,end,taxid)

if __name__ == '__main__':
        t.loadTaxonomy( sys.argv[1] if len(sys.argv)>1 else None )
        (header_new, desc, acc, start, end, tid) = ("","","","","","")
        cnt = 0
        r={}

        #for line in f:
        for line in sys.stdin:
                if line.startswith(">"):
                        cnt += 1
                        (acc, start, end, tid) = parseHeader( line )

                        length = int(end)-int(start)+1

                        if tid.endswith(".0"):
                                tid = tid.split(".")[0]
        
                        lng = t.taxid2lineageDICT(tid, 1, 1)

                        # rollup to each ranks (including strain)
                        for rank in lng:        
                                #res_tree[pid][tid] = 1
                                tid = lng[rank]['taxid']

                                # if no particular rank for this organism, use strain
                                if tid == 0:
                                        tid = lng[rank]['name'] # for example: 'Flaviviridae - no_o_rank - no_c_rank'

                                if not rank in r:
                                        r[rank]={}
        
                                if tid in r[rank]:
                                        r[rank][tid]['len'] += length
                                        r[rank][tid]['num'] += 1
                                        if length > r[rank][tid]['max']:
                                                r[rank][tid]['max'] = length
                                        elif length < r[rank][tid]['min']:
                                                r[rank][tid]['min'] = length
                                else:
                                        r[rank][tid]={}
                                        r[rank][tid]['len'] = length
                                        r[rank][tid]['num'] = 1
                                        r[rank][tid]['max'] = length
                                        r[rank][tid]['min'] = length

                #verbose
                if time.time()%10 < 1:
                        sys.stderr.write( "Processed %d sequences...\r"%(cnt) )

        sys.stderr.write("Done.\n")

        #output stats
        print( "%s\t%s\t%s\t%s\t%s\t%s" % ("Rank", "Taxid", "NumOfSeq", "Min", "Max", "TotalLength") )

        ranks = ['strain','species','genus','family','order','class','phylum','superkingdom']
        
        for rank in ranks[::-1]:
                for tid in r[rank]:
                        print( "%s\t%s\t%s\t%s\t%s\t%s" % (rank, tid, r[rank][tid]["num"], r[rank][tid]['min'], r[rank][tid]['max'], r[rank][tid]['len']) )

        sys.stderr.write( "\nComplete! Total of %d sequences processed.\n"%(cnt) )