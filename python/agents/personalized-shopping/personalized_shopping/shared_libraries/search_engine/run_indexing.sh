#!/bin/bash



python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input resources_100 \
  --index indexes_100 \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw

python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input resources_1k \
  --index indexes_1k \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw

python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input resources_10k \
  --index indexes_10k \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw

python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input resources_50k \
  --index indexes_50k \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw
