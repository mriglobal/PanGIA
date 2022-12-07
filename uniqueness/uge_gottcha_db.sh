#!/bin/bash
#$ -cwd
#$ -l h_vmem=120G
#$ -l hostname=n007
#$ -pe parallel 16
#$ -m abe
#$ -M your@email
#$ -j y
#$ -V
#$ -q all.q
#$ -S /bin/bash
#$ -N gottcha_db

set -xe

module load openmpi/gcc/64/2.1.3

export OMP_NUM_THREADS=8

RAM=120GB
INDIR=$1
OUTDIR=$2
PREFIX=$3

mpirun \
    -np $NSLOTS \
    --oversubscribe \
    -x OMP_NUM_THREADS \
    --mca btl self,sm,tcp \
  gottcha_db \
    --strain  $INDIR/$PREFIX.strain.list \
    --species $INDIR/$PREFIX.species.list \
    --genus   $INDIR/$PREFIX.genus.list \
    --family  $INDIR/$PREFIX.family.list \
    --order   $INDIR/$PREFIX.order.list \
    --class   $INDIR/$PREFIX.class.list \
    --phylum  $INDIR/$PREFIX.phylum.list \
    --kingdom $INDIR/$PREFIX.superkingdom.list \
    --strain.prefix  "strain-" \
    --species.prefix "species-" \
    --genus.prefix   "genus-" \
    --family.prefix  "family-" \
    --order.prefix   "order-" \
    --class.prefix   "class-" \
    --phylum.prefix  "phylum-" \
    --kingdom.prefix "superkingdom-" \
    --log pangia_db.log \
    --ram $RAM \
    --root $OUTDIR \
    --squash Human \
    -w 24 \
    -f 1 \
    --verbose

