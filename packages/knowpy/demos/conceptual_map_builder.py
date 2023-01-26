import sys

import pickle
import os
import numpy as np
from knowpy.misc.doc_reader import DocParser
from knowpy.models.classification.concept_classifier import ConceptClassifier
from knowpy.misc.onto_reader import get_concept_description_dict as get_ontology_concept_description_dict
from more_itertools import unique_everseen
import json
import re

ontology_path = sys.argv[1]
document_path = sys.argv[2]
result_path = sys.argv[3]

SIMILARITY_THRESHOLD = 0.6
CLUSTERING_METHOD = 'ward'
WITH_CONTEXT_INFO = True
FILTER_BY_ONTOLOGY = True
MAX_SYNTAGMA_LENGTH = 5
MIN_FREQUENCY = 3
DEFAULT_OPTIONS = {
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity':True,
	'default_tfidf_importance': 1/5,
	'lu_confidence_threshold': 3/4,
	'concept_confidence_threshold': 3/4,
}

if FILTER_BY_ONTOLOGY:
	CONCEPT_CLASSIFIER_CACHE_FILE = f"cache/[CM]{DEFAULT_OPTIONS['tf_model']}_concept_classifier_cache.pkl"
	if not os.path.isfile(CONCEPT_CLASSIFIER_CACHE_FILE):
		doc_parser = DocParser().set_document_path(document_path)
		concept_classifier = ConceptClassifier(DEFAULT_OPTIONS).set_concept_description_dict(get_ontology_concept_description_dict(ontology_path))
		concept_similarity_dict = concept_classifier.get_concept_dict(doc_parser, threshold=SIMILARITY_THRESHOLD, with_numbers=False)
		with open(CONCEPT_CLASSIFIER_CACHE_FILE, 'wb') as f:
			pickle.dump(concept_similarity_dict, f)
	else:
		with open(CONCEPT_CLASSIFIER_CACHE_FILE,'rb') as f:
			concept_similarity_dict = pickle.load(f)

	missing_concepts_counter = ConceptClassifier.get_missing_concepts_counter(concept_similarity_dict)
	found_ontology_concept_similarity_dict = {
		key: value
		for key,value in concept_similarity_dict.items()
		if key not in set(missing_concepts_counter.keys())
	}
	found_ontology_concept_list = list(found_ontology_concept_similarity_dict.keys())
	print('Found concepts:')
	print(json.dumps(found_ontology_concept_similarity_dict, indent=4, sort_keys=True))
	print('Missing concepts:')
	missing_concepts_counter = sorted(missing_concepts_counter.items(), key=lambda x: x[1], reverse=True)
	missing_concepts_counter = dict(missing_concepts_counter)
	print(json.dumps(missing_concepts_counter, indent=4))


CACHE_FILE = DEFAULT_OPTIONS['tf_model']+'_cache.pkl'
if os.path.isfile(CACHE_FILE):
	with open(CACHE_FILE,'rb') as f:
		concept_dict = pickle.load(f)
else:
	doc_parser = DocParser().set_document_path(document_path)
	concept_dict = ConceptClassifier(DEFAULT_OPTIONS).set_concept_description_dict(get_ontology_concept_description_dict(ontology_path)).get_concept_embedding(doc_parser, with_sentence_embedding=True)
	with open(CACHE_FILE,'wb') as f:
		pickle.dump(concept_dict, f)

concept_dict = {
	k:v 
	for k,v in concept_dict.items() 
	if k.lower().strip().count(' ') < MAX_SYNTAGMA_LENGTH
	#and re.search(r'\d',k) is None
	and (k.lower().strip() in found_ontology_concept_list or v['count'] >= MIN_FREQUENCY)
}
print('Unique Concepts:', len(concept_dict))
concept_label_list, concept_value_list = zip(*concept_dict.items())
if WITH_CONTEXT_INFO:
	concept_embedding_list = list(map(
		lambda x: np.concatenate(
			(
				x['embedding'], 
				np.mean(x['sentence_embedding_list'], axis=0),
				np.std(x['sentence_embedding_list'], axis=0),
			),
			axis=-1,
		).flatten(), 
		concept_value_list
	))
else:
	concept_embedding_list = list(map(lambda x: np.array(x['embedding']).flatten(), concept_value_list))
print('Concept embedding shape:', concept_embedding_list[0].shape)

from misc.tree_cluster_builder import build_hierarchical_cluster, get_most_similar_leaf, build_edge_list
from misc.graph_builder import save_graph, filter_graph_by_root_set

if FILTER_BY_ONTOLOGY:
	old_cophentic_correlation_distance = None
	cophentic_correlation_distance = 0
	while old_cophentic_correlation_distance != cophentic_correlation_distance:
		old_cophentic_correlation_distance = cophentic_correlation_distance
		dendrogram, cophentic_correlation_distance = build_hierarchical_cluster(concept_embedding_list, concept_label_list, method=CLUSTERING_METHOD)
		print('Cophentic Correlation Distance:', cophentic_correlation_distance)
		edge_list = build_edge_list(dendrogram)
		# Keep only edges related to ontology concepts
		edge_list = filter_graph_by_root_set(edge_list, found_ontology_concept_list)
		edge_list = unique_everseen(edge_list)
		edge_list = list(edge_list)
		
		remaining_concepts = set(map(lambda x: x[0], edge_list)).union(map(lambda x: x[-1], edge_list))
		remaining_embedding_list = []
		remaining_label_list = []
		for embedding, label in zip(concept_embedding_list, concept_label_list):
			if label not in remaining_concepts:
				continue
			remaining_embedding_list.append(embedding)
			remaining_label_list.append(label)
		concept_embedding_list = remaining_embedding_list
		concept_label_list = remaining_label_list
		print('Triple count:', len(edge_list))

save_graph(edge_list, result_path, max(min(256,len(edge_list)/2),32))
