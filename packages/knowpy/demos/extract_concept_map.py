import json
import os
import sys
from itertools import islice

explainable_information_path = sys.argv[1]
cache_path = sys.argv[2]
main_aspect = sys.argv[3]
if not os.path.exists(cache_path): os.mkdir(cache_path)

from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder
from knowpy.models.estimation.explainability_estimator import ExplainabilityEstimator
from knowpy.models.reasoning.question_answerer import QuestionAnswerer
from knowpy.models.knowledge_extraction.question_answer_extractor import QuestionAnswerExtractor
from knowpy.misc.doc_reader import load_or_create_cache
from knowpy.misc.graph_builder import get_betweenness_centrality, save_graph, get_concept_set, get_concept_description_dict, save_graphml
from knowpy.misc.jsonld_lib import *

import networkx as nx
from knowpy.misc.adjacency_matrix import AdjacencyMatrix
from more_itertools import unique_everseen

NUMBER_OF_MOST_IMPORTANT_ASPECTS_TO_INCLUDE_IN_SUMMARY = 30

archetype_weight_dict = {
	'why': 1,
	'how': 0.9,
	'what-for': 0.75,
	'what': 0.75,
	'what-if': 0.6,
	'when': 0.5,
}

################ Configuration ################
ARCHETYPE_FITNESS_OPTIONS = {
	'only_overview_exploration': False,
	'answer_pertinence_threshold': 0.15, 
	'answer_to_question_similarity_threshold': 0.9502, 
	'answer_to_answer_similarity_threshold': 0.9502, 
}
OVERVIEW_OPTIONS = {
	'answer_pertinence_threshold': None, # default is None
	'answer_to_question_similarity_threshold': None, # default is 0.9502
	'answer_to_answer_similarity_threshold': None, # default is 0.9502
	'minimise': False,
	'sort_archetypes_by_relevance': False,
	'set_of_archetypes_to_consider': None, # set(['why','how'])
	'answer_horizon': 10,
	'remove_duplicate_answer_sentences': True,

	'top_k': 100,
	'include_super_concepts_graph': False, 
	'include_sub_concepts_graph': True, 
	'add_external_definitions': False, 
	'consider_incoming_relations': True,
	'tfidf_importance': 0,
}

QA_EXTRACTOR_OPTIONS = {
	'models_dir': '/home/toor/Desktop/data/models', 
	# 'models_dir': '/Users/toor/Documents/University/PhD/Project/YAI/code/libraries/QuAnsX/data/models', 
	'use_cuda': False,

	'sbert_model': {
		'url': 'facebook-dpr-question_encoder-multiset-base', # model for paraphrase identification
		'cache_dir': '/Users/toor/Documents/Software/DLModels/sb_cache_dir/',
		'use_cuda': False,
	},
}

ONTOLOGY_BUILDER_DEFAULT_OPTIONS = {
	'spacy_model': 'en_core_web_trf',
	'n_threads': 1,
	'use_cuda': False,

	'max_syntagma_length': None,
	'lemmatize_label': False,

	'default_similarity_threshold': 0.75,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
		'use_cuda': False,
	},
	'with_centered_similarity': True,
}

CONCEPT_CLASSIFIER_DEFAULT_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': False,

	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
		'use_cuda': False,
	},
	'with_centered_similarity': True,
	'default_similarity_threshold': 0.75,
	# 'default_tfidf_importance': 3/4,
}

SENTENCE_CLASSIFIER_DEFAULT_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': False,

	'tf_model': {
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder-qa2/3', # English QA
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3', # Multilingual QA # 16 languages (Arabic, Chinese-simplified, Chinese-traditional, English, French, German, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Spanish, Thai, Turkish, Russian)
		# 'url': 'https://tfhub.dev/google/LAReQA/mBERT_En_En/1',
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
		'use_cuda': False,
	}, 
	# 'sbert_model': {
	# 	'url': 'facebook-dpr-question_encoder-multiset-base', # model for paraphrase identification
	# 	'use_cuda': False,
	# },
	'with_centered_similarity': False,
	'with_topic_scaling': False,
	'with_stemmed_tfidf': False,
	# 'default_tfidf_importance': 1/4,
}

########################################################################
print('Building Graph..')
explainable_information_graph = load_or_create_cache(
	os.path.join(cache_path,f"cache_explainable_information_graph_lemma-{ONTOLOGY_BUILDER_DEFAULT_OPTIONS['lemmatize_label']}.pkl"), 
	lambda: OntologyBuilder(ONTOLOGY_BUILDER_DEFAULT_OPTIONS).set_documents_path(explainable_information_path).build()
)
save_graphml(explainable_information_graph, os.path.join(cache_path,'knowledge_graph'))
print('Graph size:', len(explainable_information_graph))
print("Graph's Clauses:", len(list(filter(lambda x: '{obj}' in x[1], explainable_information_graph))))

#############
print('Building Question Answerer..')
betweenness_centrality = load_or_create_cache(
	os.path.join(cache_path,'cache_betweenness_centrality.pkl'), 
	lambda: get_betweenness_centrality(filter(lambda x: '{obj}' in x[1], explainable_information_graph))
)

qa_cache = os.path.join(cache_path,'cache_qa_embedder.pkl')
qa = QuestionAnswerer( # Using qa_dict_list also for getting the archetype_fitness_dict might over-estimate the median pertinence of some archetypes (and in a different way for each), because the QA Extractor is set to prefer a higher recall to a higher precision.
	graph= explainable_information_graph, 
	concept_classifier_options= CONCEPT_CLASSIFIER_DEFAULT_OPTIONS, 
	sentence_classifier_options= SENTENCE_CLASSIFIER_DEFAULT_OPTIONS, 
	# answer_summariser_options= SUMMARISER_DEFAULT_OPTIONS,
	betweenness_centrality= betweenness_centrality,
)
qa.load_cache(qa_cache)
qa.store_cache(qa_cache)
########################################################

# important_aspects = get_concept_description_dict(graph=explainable_information_graph, label_predicate=HAS_LABEL_PREDICATE, valid_concept_filter_fn=lambda x: '{obj}' in x[1]).keys()
# important_aspects = filter(qa.is_relevant_aspect, important_aspects)
# important_aspects = set(important_aspects)
important_aspects = qa.relevant_aspect_set
important_aspects = list(important_aspects)
print('Important aspects:', len(important_aspects))
print(json.dumps(important_aspects, indent=4))

explainability_estimator_cache = os.path.join(cache_path,'cache_explainability_estimator.pkl')
explainability_estimator = ExplainabilityEstimator(qa)

#############
aspect_archetype_answers_dict = load_or_create_cache(
	explainability_estimator_cache+'.aspect_archetype_answers_dict.pkl',
	lambda: explainability_estimator.extract_archetypal_answers_per_aspect(aspect_uri_list=important_aspects, **dict(OVERVIEW_OPTIONS))
)

aspect_WeDoX_dict = load_or_create_cache(
	explainability_estimator_cache+'.aspect_WeDoX_dict.pkl',
	lambda: explainability_estimator.get_aspect_WeDoX_dict(aspect_archetype_answers_dict, OVERVIEW_OPTIONS, ARCHETYPE_FITNESS_OPTIONS, archetype_weight_dict)
)

sorted_aspect_WeDoX_dict = dict(sorted(aspect_WeDoX_dict.items(), key=lambda x:x[-1], reverse=True))
print('Aspects WeDoX Ranking:', json.dumps(sorted_aspect_WeDoX_dict, indent=4))

qa.store_cache(qa_cache)
#############

# qa_dict_list = load_or_create_cache(
# 	explainability_estimator_cache+'.qa_dict_list.pkl',
# 	lambda: QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS).extract(explainable_information_graph)
# )
explainable_information_abstract_WeDoX_dict = load_or_create_cache(
	explainability_estimator_cache+'.abstract_WeDoX_dict.pkl',
	lambda: explainability_estimator.get_abstract_WeDoX_dict(aspect_WeDoX_dict)
)
print('Abstract WeDoX:', json.dumps(explainable_information_abstract_WeDoX_dict, indent=4))

aspects_sorted_by_importance = list(explainable_information_abstract_WeDoX_dict.keys())
most_important_aspect_set = set(aspects_sorted_by_importance[:NUMBER_OF_MOST_IMPORTANT_ASPECTS_TO_INCLUDE_IN_SUMMARY])

concept_map_edge_list = qa.adjacency_matrix.get_paths_to_target(
	source=main_aspect, 
	target_set=most_important_aspect_set, 
	direction_set=['in','out'],
	predicate_filter_fn=lambda x: '{obj}' in x,
)
concept_set = get_concept_set(concept_map_edge_list)
print('Concept Map Edges:', len(concept_map_edge_list))
print('Concept Map Nodes:', len(concept_set))

def summarise_unweighted_graph_passing_by_nodes(edge_list, nodes, node_importance_fn=lambda x:x, equivalence_relation_set=None):
	nx_digraph = nx.DiGraph() # directed graph
	nx_graph = nx.Graph() # undirected graph
	for s,p,o in filter(lambda x: '{obj}' in x[1], edge_list):
		nx_digraph.add_edge(s,o)
		nx_graph.add_edge(s,o)
	adjacency_matrix = AdjacencyMatrix(edge_list, equivalence_relation_set=equivalence_relation_set)
	summarised_edge_list = []
	for j,main_aspect in enumerate(nodes):
		for target_aspect in nodes[j+1:]:
			paths = []
			try:
				paths += list(nx.all_shortest_paths(nx_digraph, main_aspect, target_aspect))
			except:
				pass
			try:
				paths += list(nx.all_shortest_paths(nx_digraph, target_aspect, main_aspect))
			except:
				pass
			if not paths:
				paths = list(nx.all_shortest_paths(nx_graph, main_aspect, target_aspect))
			best_shortest_path = max(
				paths, 
				key=lambda x: sum(map(node_importance_fn,x))
			)
			# print(best_shortest_path)
			for i in range(len(best_shortest_path)-1):
				summarised_edge_list += adjacency_matrix.get_edges_between_nodes(best_shortest_path[i],best_shortest_path[i+1])
	return list(unique_everseen(summarised_edge_list))
def summarise_unweighted_graph_passing_by_nodes_centred_on_main_aspect(edge_list, nodes, main_aspect, node_importance_fn=lambda x:x, equivalence_relation_set=None):
	nx_digraph = nx.DiGraph() # directed graph
	nx_graph = nx.Graph() # undirected graph
	for s,p,o in filter(lambda x: '{obj}' in x[1], edge_list):
		nx_digraph.add_edge(s,o)
		nx_graph.add_edge(s,o)
	adjacency_matrix = AdjacencyMatrix(edge_list, equivalence_relation_set=equivalence_relation_set)
	
	# nodes_to_remove = set()
	# for j,n1 in enumerate(nodes):
	# 	for n2 in nodes[j+1:]:
	# 		subclass_relation_iter = filter(lambda x: x[1]==SUBCLASSOF_PREDICATE, adjacency_matrix.get_edges_between_nodes(n1,n2))
	# 		for _,_,o in subclass_relation_iter:
	# 			nodes_to_remove.add(o)

	summarised_edge_list = []
	for target_aspect in nodes:
		if target_aspect == main_aspect:
			continue
		# if target_aspect in nodes_to_remove:
		# 	continue
		paths = []
		try:
			paths += list(nx.all_shortest_paths(nx_digraph, main_aspect, target_aspect))
		except:
			pass
		try:
			paths += list(nx.all_shortest_paths(nx_digraph, target_aspect, main_aspect))
		except:
			pass
		if not paths:
			paths += list(nx.all_shortest_paths(nx_graph, main_aspect, target_aspect))
		best_shortest_path = max(
			paths, 
			key=lambda x: sum(map(node_importance_fn,x))
		)
		# print(best_shortest_path)
		for i in range(len(best_shortest_path)-1):
			summarised_edge_list += adjacency_matrix.get_edges_between_nodes(best_shortest_path[i],best_shortest_path[i+1])
	return list(unique_everseen(summarised_edge_list))
def format_concept_map(graph, summarised_graph, equivalence_relation_set=None):
	adjacency_matrix = AdjacencyMatrix(graph, equivalence_relation_set=equivalence_relation_set)
	# merge subclasses 
	nodes = list(get_concept_set(summarised_graph))
	equivalence_dict = {
		t:set([t])
		for t in nodes
	}
	for j,t1 in enumerate(nodes):
		for t2 in nodes[j+1:]:
			for s,p,o in adjacency_matrix.get_edges_between_nodes(t1,t2):
				if SUBCLASSOF_PREDICATE == p:
					equivalence_dict[s].add(o)
	
	def recursive_merge(d, keys_to_update=None):
		if not keys_to_update:
			keys_to_update = d.keys()
		new_keys_to_update = set()
		for k in keys_to_update:
			for c in d[k]:
				if c == k: 
					continue
				old_len = len(d[c])
				d[c] |= d[k]
				if len(d[c]) != old_len:
					new_keys_to_update |= d[c]
		if new_keys_to_update:
			recursive_merge(d, new_keys_to_update)
	recursive_merge(equivalence_dict)
	equivalence_dict = {
		k:sorted(v)
		for k,v in equivalence_dict.items()
	}

	summarised_graph = (
		(
			', '.join(map(qa.get_label, equivalence_dict.get(s,[s]))),
			list(qa.get_source_label_set(s).intersection(qa.get_source_label_set(p)).intersection(qa.get_source_label_set(o))), 
			', '.join(map(qa.get_label, equivalence_dict.get(o,[o]))),
		)
		for s,p,o in summarised_graph
	)
	summarised_graph = filter(lambda x: x[0]!=x[-1] and x[1], summarised_graph)
	return list(unique_everseen(summarised_graph))
summarised_concept_map_edge_list = summarise_unweighted_graph_passing_by_nodes(
	explainable_information_graph, 
	list(unique_everseen([main_aspect]+aspects_sorted_by_importance[:NUMBER_OF_MOST_IMPORTANT_ASPECTS_TO_INCLUDE_IN_SUMMARY])),
	# main_aspect,
	node_importance_fn=lambda y: explainable_information_abstract_WeDoX_dict.get(y,-1),
	equivalence_relation_set=set([IS_EQUIVALENT]),
)
summarised_concept_set = get_concept_set(summarised_concept_map_edge_list)
print('Summarised Concept Map Edges:', len(summarised_concept_map_edge_list))
print('Summarised Concept Map Nodes:', len(summarised_concept_set))

print('Edge Compression Ratio:', len(summarised_concept_map_edge_list)/len(concept_map_edge_list))
print('Node Compression Ratio:', len(summarised_concept_set)/len(concept_set))

# map(get_string_from_triple,summarised_concept_map_edge_list)s
formatted_concept_map = format_concept_map(
	graph=explainable_information_graph, 
	summarised_graph=summarised_concept_map_edge_list, 
	equivalence_relation_set=set([IS_EQUIVALENT])
)
# print(json.dumps(formatted_concept_map, indent=4))
save_graph(formatted_concept_map, os.path.join(cache_path,'concept_map'), 100)

#############
# aspect_importance_dict = dict(islice(sorted_aspect_WeDoX_dict.items(),NUMBER_OF_MOST_IMPORTANT_ASPECTS_TO_INCLUDE_IN_SUMMARY))

