#!/usr/bin/bash
function join_by { local IFS="$1"; shift; echo "$*"; }

INDIR="pangia_db_signature_indir"
TAXA_DIR="pangia_database"
PANGIA_DB_DIR="pangia_database"
OUTDIR="pangia_db_signature"
PREFIX="pangia_db_signature.gottcha_db"

alias qsubbin='qsub -S /bin/sh -V -cwd -b y -j y -m abe -M your@email'

mkdir -p $INDIR
parallel "cat pangia_Refseq_*/*.gottcha_db.{}.list > $INDIR/pangia_db_signature.gottcha_db.{}.list" ::: superkingdom phylum class order family genus species strain

# generate signatures
JID=`qsub uge_gottcha_db.sh $INDIR $OUTDIR $PREFIX`
JID=`echo $JID | awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}'`

# summarize signature length
JOBIDS=()
for RANK in strain species genus family order class phylum superkingdom
do
    JID=`qsubbin -pe smp 2 -l h_vmem=20G -N pandb-sig-$RANK " \
          find pangia_db_signature/ -name '$RANK-*.fna' -exec cat {} \; \
          | grep '^>' \
          | scripts/signature_summary.py $TAXA_DIR \
          > pangia_db_signature.$RANK.summary.txt \
          2> pangia_db_signature.$RANK.summary.log"`

    JOBIDS+=(`echo $JID | awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}'`)
done

# merge to an uniqueness metrics
SUMJIDS=`join_by , "${JOBIDS[@]}"`

qsubbin -pe parallel 32 -l h_vmem=20G -N pandb-merge -hold_jid $SUMJIDS \
    cat $PANGIA_DB_DIR/NCBI_genomes_refseq89_*.fa.ann \
    | scripts/pangia_uniqueness_metrics.py $TAXA_DIR pangia_db_signature.*.summary.txt \
    > uniqueness.tsv