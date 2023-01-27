import sched, time
import json
import math
from os import mkdir, path as os_path
base_path = os_path.dirname(os_path.abspath(__file__))
cache_path = os_path.join(base_path,'cache','edu')
document_path = os_path.join(base_path,'documents','edu')

# from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder
from knowpy.models.knowledge_extraction.knowledge_graph_builder import KnowledgeGraphBuilder
from knowpy.models.reasoning.question_answerer import QuestionAnswerer
from knowpy.models.reasoning.question_answerer_naive import QuestionAnswererNaive
from knowpy.models.reasoning.adaptive_question_answerer import AdaptiveQuestionAnswerer
from knowpy.models.knowledge_extraction.knowledge_graph_manager import KnowledgeGraphManager
from knowpy.models.knowledge_extraction.couple_extractor import filter_invalid_sentences

from knowpy.models.knowledge_extraction.question_answer_extractor import QuestionAnswerExtractor
from knowpy.misc.doc_reader import load_or_create_cache, DocParser, get_document_list
from knowpy.misc.graph_builder import get_concept_description_dict, get_betweenness_centrality, save_graphml
from knowpy.misc.levenshtein_lib import labels_are_contained, remove_similar_labels
from knowpy.misc.utils import *
from more_itertools import unique_everseen
from tqdm import tqdm
from pathos.multiprocessing import ProcessingPool as Pool

import sys
import logging
logger = logging.getLogger('knowpy')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler(sys.stdout))

# import sys
# _,information_units,model_family = sys.argv

# information_units = information_units.casefold()
# model_family = model_family.casefold()

MAX_HISTORY_LEN = 0
WITH_ANNOTATIONS = False
ADAPTIVE_QA = True
DOCUMENTS_PER_CHUNK = 2**9
PARAGRAPHS_PER_CHUNK = 2**15
EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES = False # set it to True to reduce the number of considered Q/A and memory footprint
AVOID_JUMPS = True
AVOID_COREFERENCING = False

MIN_EXPLAINABILITY= 0.55

ADAPTIVITY_OPTIONS= {
	'remove_old_content': False, 
	'old_content_confidence_scaling_factor': 0.66,
}

OPTIMAL_ARCHETYPE_IDENTIFICATION_OPTIONS = {
	'max_question_length': 50,
	'valid_question_type_set': set([
		'disco', # elementary discourse units
		'qaamr', # abstract meaning representations
	]),
	'question_to_question_max_similarity_threshold': 1,
	'explanatory_sentence_horizon': 10,
}

OVERVIEW_OPTIONS = {
	'answer_horizon': 2,
	'question_horizon': 4,
	######################
	## QuestionAnswerer stuff
	'tfidf_importance': 0,
	'answer_pertinence_threshold': 0.57, 
	'answer_to_question_max_similarity_threshold': None,
	'answer_to_answer_max_similarity_threshold': 0.85,
	'use_weak_pointers': False,
	'top_k': 2,
	######################
	'keep_the_n_most_similar_concepts': 1, 
	'query_concept_similarity_threshold': 0.55, 
	'include_super_concepts_graph': False, 
	'include_sub_concepts_graph': True, 
	'consider_incoming_relations': True,
	######################
	'sort_archetypes_by_relevance': True, 
	'minimise': True, 
}

DOX_OPTIONS = dict(OVERVIEW_OPTIONS)
DOX_OPTIONS.update({
	######################
	## ExplainabilityEstimator stuff
	'set_of_archetypes_to_consider': None, # set(['why','how'])
	'answer_horizon': None,
	'remove_duplicate_answer_sentences': True,
	######################
	## QuestionAnswerer stuff
	'tfidf_importance': 0,
	'use_weak_pointers': False,
	'answer_pertinence_threshold': None, 
	'answer_to_question_max_similarity_threshold': None,
	'answer_to_answer_max_similarity_threshold': None,
	'top_k': 100,
	######################
})

ARCHETYPE_FITNESS_OPTIONS = {
	'only_overview_exploration': False,
	'answer_pertinence_threshold': 0.15, 
	'answer_to_question_max_similarity_threshold': None,
	'answer_to_answer_max_similarity_threshold': 0.85,
}

OQA_OPTIONS = {
	'answer_horizon': 20,
	######################
	## QuestionAnswerer stuff
	'answer_pertinence_threshold': 0.15, 
	'tfidf_importance': 1/2,
	'answer_to_question_max_similarity_threshold': None,
	'answer_to_answer_max_similarity_threshold': 0.85,
	'use_weak_pointers': False,
	'top_k': 100,

	'keep_the_n_most_similar_concepts': 2, 
	'query_concept_similarity_threshold': 0.55, 
	'add_external_definitions': False, 
	'include_super_concepts_graph': True, 
	'include_sub_concepts_graph': True, 
	'consider_incoming_relations': True,
}

QA_EXTRACTOR_OPTIONS = {
	'models_dir': 'question_extractor/data/models', 

	# 'sbert_model': {
	# 	'url': 'facebook-dpr-question_encoder-multiset-base', # model for paraphrase identification
	# 	'use_cuda': True,
	# },
	'tf_model': {
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder-qa2/3', # English QA
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3', # Multilingual QA # 16 languages (Arabic, Chinese-simplified, Chinese-traditional, English, French, German, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Spanish, Thai, Turkish, Russian)
		# 'url': 'https://tfhub.dev/google/LAReQA/mBERT_En_En/1',
		# 'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
		# 'use_cuda': True,
	}, 

	# 'with_cache': False,
	'with_tqdm': True,
	'use_cuda': True,
	'default_batch_size': 10,
	'default_cache_dir': cache_path,
	'generate_kwargs': {
		"max_length": 128,
		"num_beams": 10,
		# "num_return_sequences": 1,
		# "length_penalty": 1.5,
		# "no_repeat_ngram_size": 3, # do not set it when answer2question=False, questions always start with the same ngrams 
		"early_stopping": True,
	},
	'e2e_generate_kwargs': {
		"max_length": 128,
		"num_beams": 10,
		# "num_beam_groups": 1,
		"num_return_sequences": 10,
		# "length_penalty": 1.5,
		# "no_repeat_ngram_size": 3, # do not set it when answer2question=False, questions always start with the same ngrams 
		"early_stopping": True,
		# "return_dict_in_generate": True,
		# "forced_eos_token_id": True
	},
	'task_list': [
		'answer2question', 
		'question2answer'
	],
}

QA_CLEANING_OPTIONS = {
	# 'sorted_template_list': None, 
	'min_qa_pertinence': 0, 
	'max_qa_similarity': 1, 
	# 'max_answer_to_question_similarity': 0.9502, 
	'min_answer_to_sentence_overlap': 0.75,
	'min_question_to_sentence_overlap': 0.5,
	'max_answer_to_question_overlap': 0.75,
	'coreference_resolution': False,
}

KG_MANAGER_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': True,
	'with_cache': False,
	'with_tqdm': False,

	'min_sentence_len': 150,
	'max_paragraph_len': 1000,
}

GRAPH_BUILDER_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': True,

	'with_cache': False,
	'with_tqdm': True,

	'max_syntagma_length': None,
	'add_source': True,
	'add_label': True,
	'lemmatize_label': False,

	# 'default_similarity_threshold': 0.75,
	'default_similarity_threshold': 0,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		# 'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
		# 'use_cuda': True,
		# 'with_cache': True,
		# 'batch_size': 100,
	},
	'with_centered_similarity': True,
}

CONCEPT_CLASSIFIER_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': True,

	'default_batch_size': 20,
	'with_tqdm':True,

	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		# 'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	# 'sbert_model': {
	# 	'url': 'all-MiniLM-L12-v2',
	# 	'use_cuda': True,
	# },
	'with_centered_similarity': True,
	'default_similarity_threshold': 0.75,
	# 'default_tfidf_importance': 3/4,
	'default_tfidf_importance': 0,
}

SENTENCE_CLASSIFIER_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': True,

	# 'default_batch_size': 100,
	'with_tqdm':True,
	'with_cache': False,
	
	'with_centered_similarity': False,
	'with_topic_scaling': False,
	'with_stemmed_tfidf': False,
	'default_tfidf_importance': 0,
}

SUMMARISER_OPTIONS = {
	# 'spacy_model': 'en_core_web_trf',
	# 'n_threads': 1,
	# 'use_cuda': True,

	'hf_model': {
		# 'url': 't5-base',
		'url': 'facebook/bart-large-cnn', # baseline
		# 'url': 'google/pegasus-billsum',
		# 'url': 'sshleifer/distilbart-cnn-12-6', # speedup (over the baseline): 1.24
		# 'url': 'sshleifer/distilbart-cnn-12-3', # speedup (over the baseline): 1.78
		# 'url': 'sshleifer/distilbart-cnn-6-6', # speedup (over the baseline): 2.09
		# 'cache_dir': '/Users/toor/Documents/Software/DLModels/hf_cache_dir/',
		'framework': 'pt',
		# 'use_cuda': False,
	},
}

################ Initialise data structures ################
def init(model_family, information_units):
	using_special_graph = 'edu' in information_units or 'amr' in information_units
	normal_graph_without_jumps = using_special_graph or AVOID_JUMPS
	with_qa_dict_list = using_special_graph or ADAPTIVE_QA
	print(f'server_interface {model_family} {information_units}, with with_qa_dict_list: {with_qa_dict_list}')
	graph_cache = os_path.join(cache_path,f"graph_clauses_lemma-{GRAPH_BUILDER_OPTIONS['lemmatize_label']}_jumps-{not normal_graph_without_jumps}.pkl")
	edu_graph_cache = os_path.join(cache_path,f"graph_edu_lemma-{GRAPH_BUILDER_OPTIONS['lemmatize_label']}_paragraphs-{EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES}_jumps-{not AVOID_JUMPS}.pkl")
	edu_disco_only_graph_cache = os_path.join(cache_path,f"graph_edu_disco_only_lemma-{GRAPH_BUILDER_OPTIONS['lemmatize_label']}_paragraphs-{EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES}_jumps-{not AVOID_JUMPS}.pkl")
	edu_amr_only_graph_cache = os_path.join(cache_path,f"graph_edu_amr_only_lemma-{GRAPH_BUILDER_OPTIONS['lemmatize_label']}_paragraphs-{EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES}_jumps-{not AVOID_JUMPS}.pkl")
	# betweenness_centrality_cache = os_path.join(cache_path,'betweenness_centrality.pkl')
	qa_dict_list_cache = os_path.join(cache_path,f'qa_dict_list_{EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES}.pkl')
	cleaned_qa_dict_list_cache = os_path.join(cache_path,f'cleaned_qa_dict_list_{EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES}.pkl')
	filtered_qa_dict_list_cache = os_path.join(cache_path,f'filtered_qa_dict_list_{EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES}.pkl')
	qa_cache = os_path.join(cache_path,f'{"adaptive_" if ADAPTIVE_QA else ""}qa_embedder-{"clause_edu"}.pkl')

	################ Configuration ################
	if model_family == 'tf':
		SENTENCE_CLASSIFIER_OPTIONS['tf_model'] = {
			# 'url': 'https://tfhub.dev/google/universal-sentence-encoder-qa/3', # English QA
			'url': 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3', # Multilingual QA # 16 languages (Arabic, Chinese-simplified, Chinese-traditional, English, French, German, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Spanish, Thai, Turkish, Russian)
			# 'url': 'https://tfhub.dev/google/LAReQA/mBERT_En_En/1',
			# 'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
			'use_cuda': True,
			'with_cache': True,
		}
	elif model_family == 'fb':
		SENTENCE_CLASSIFIER_OPTIONS['sbert_model'] = {
			'url': 'multi-qa-MiniLM-L6-cos-v1', # model for paraphrase identification
			'use_cuda': True,
			'with_cache': True,
		}
		# Model								Performance Semantic Search (6 Datasets)	Queries (GPU / CPU) per sec.
		# multi-qa-MiniLM-L6-cos-v1			51.83										18,000 / 750
		# multi-qa-distilbert-cos-v1		52.83										7,000 / 350
		# multi-qa-mpnet-base-cos-v1		57.46										4,000 / 170


	########################################################################
	def extract_graph():
		print('Building Graph..')
		document_list = get_document_list(document_path)
		chunks = tuple(get_chunks(document_list, elements_per_chunk=DOCUMENTS_PER_CHUNK))
		num_chunks = math.ceil(len(document_list)/DOCUMENTS_PER_CHUNK)
		del document_list
		kg_builder = KnowledgeGraphBuilder(GRAPH_BUILDER_OPTIONS)
		# kg_builder = OntologyBuilder(GRAPH_BUILDER_OPTIONS)
		for i,docs in enumerate(tqdm(chunks)):
			load_or_create_cache(graph_cache+f'.{i}_{num_chunks}_{normal_graph_without_jumps}.pkl', lambda: kg_builder.set_document_list(docs, avoid_jumps=not normal_graph_without_jumps).build(add_verbs=False, add_predicates_label=False))
		graph = []
		for i,docs in enumerate(tqdm(chunks)):
			graph += load_or_create_cache(graph_cache+f'.{i}_{num_chunks}_{normal_graph_without_jumps}.pkl', lambda: kg_builder.set_document_list(docs, avoid_jumps=not normal_graph_without_jumps).build(add_verbs=False, add_predicates_label=False))
			graph = list(unique_everseen(graph))
		return graph
	graph = load_or_create_cache(graph_cache, extract_graph)
	# graph = load_or_create_cache(
	# 	graph_cache, 
	# 	lambda: OntologyBuilder(GRAPH_BUILDER_OPTIONS).set_documents_path(document_path).build()
	# )
	# save_graphml(graph, 'knowledge_graph')
	print('Graph size:', len(graph))
	print('Grammatical Clauses:', len(list(filter(lambda x: '{obj}' in x[1], graph))))
	########################################################################
	print('Building Question Answerer..')
	# betweenness_centrality = load_or_create_cache(
	# 	betweenness_centrality_cache, 
	# 	lambda: get_betweenness_centrality(filter(lambda x: '{obj}' in x[1], graph))
	# )

	if with_qa_dict_list:
		qa_dict_list = load_or_create_cache(qa_dict_list_cache, lambda: QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS).extract(graph, cache_path=qa_dict_list_cache, use_paragraph_text=EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES))
		print(f'qa_dict_list now has len {len(qa_dict_list)}')
		qa_dict_list = load_or_create_cache(cleaned_qa_dict_list_cache, lambda: QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS).clean_qa_dict_list(qa_dict_list, cache_path=cleaned_qa_dict_list_cache, **QA_CLEANING_OPTIONS))
		print(f'qa_dict_list now has len {len(qa_dict_list)}')
		qa_dict_list = load_or_create_cache(filtered_qa_dict_list_cache, lambda: filter_invalid_sentences(QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS), qa_dict_list, key=lambda x: x['sentence'], avoid_coreferencing=AVOID_COREFERENCING))
		print(f'qa_dict_list now has len {len(qa_dict_list)}')

	edu_graph = None
	if 'edu_amr' in information_units or 'amr_edu' in information_units:
		edu_graph = load_or_create_cache(
			edu_graph_cache, 
			lambda: QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS).extract_aligned_graph_from_qa_dict_list(
				graph, 
				GRAPH_BUILDER_OPTIONS, 
				qa_dict_list=qa_dict_list,
				elements_per_chunk=PARAGRAPHS_PER_CHUNK,
				avoid_jumps=AVOID_JUMPS,
				cache_path=edu_graph_cache,
				add_verbs=False, 
				add_predicates_label=False, 
				use_paragraph_text=EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES,
			)
		)
	elif 'edu' in information_units:
		edu_graph = load_or_create_cache(
			edu_disco_only_graph_cache, 
			lambda: QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS).extract_aligned_graph_from_qa_dict_list(
				graph, 
				GRAPH_BUILDER_OPTIONS, 
				qa_dict_list=qa_dict_list,
				qa_type_to_use= [
					'disco', # elementary discourse units
					# 'qaamr', # abstract meaning representations
				],
				elements_per_chunk=PARAGRAPHS_PER_CHUNK,
				avoid_jumps=AVOID_JUMPS,
				cache_path=edu_disco_only_graph_cache,
				add_verbs=False, 
				add_predicates_label=False, 
				use_paragraph_text=EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES,
			)
		)
	elif 'amr' in information_units:
		edu_graph = load_or_create_cache(
			edu_amr_only_graph_cache, 
			lambda: QuestionAnswerExtractor(QA_EXTRACTOR_OPTIONS).extract_aligned_graph_from_qa_dict_list(
				graph, 
				GRAPH_BUILDER_OPTIONS, 
				qa_dict_list=qa_dict_list,
				qa_type_to_use= [
					# 'disco', # elementary discourse units
					'qaamr', # abstract meaning representations
				],
				elements_per_chunk=PARAGRAPHS_PER_CHUNK,
				avoid_jumps=AVOID_JUMPS,
				cache_path=edu_amr_only_graph_cache,
				add_verbs=False, 
				add_predicates_label=False, 
				use_paragraph_text=EXTRACT_QA_USING_PARAGRAPHS_INSTEAD_OF_SENTENCES,
			)
		)
	if edu_graph is None:
		kg_manager = KnowledgeGraphManager(KG_MANAGER_OPTIONS, graph)
	else:
		kg_manager = KnowledgeGraphManager.build_from_edus_n_clauses(
			KG_MANAGER_OPTIONS,
			graph= graph, 
			# qa_dict_list= qa_dict_list, 
			# kg_builder_options = GRAPH_BUILDER_OPTIONS,
			# qa_extractor_options= QA_EXTRACTOR_OPTIONS,
			use_only_elementary_discourse_units= ('clause' not in information_units),
			edu_graph= edu_graph,
			# qa_type_to_use= [
			# 	'disco', # elementary discourse units
			# 	'qaamr', # abstract meaning representations
			# ],
		)
		del edu_graph
	del graph

	if ADAPTIVE_QA:
		qa = AdaptiveQuestionAnswerer(
			kg_manager= kg_manager, 
			qa_dict_list= qa_dict_list,
			concept_classifier_options= CONCEPT_CLASSIFIER_OPTIONS, 
			sentence_classifier_options= SENTENCE_CLASSIFIER_OPTIONS, 
			answer_summariser_options= SUMMARISER_OPTIONS, 
			# betweenness_centrality=None, 
			min_explainability= MIN_EXPLAINABILITY,
			dox_options= DOX_OPTIONS, 
			archetype_fitness_options= ARCHETYPE_FITNESS_OPTIONS, 
			archetype_weight_dict= None,
		)
	else:
		if with_qa_dict_list: del qa_dict_list
		qa = QuestionAnswerer(
			kg_manager= kg_manager, 
			concept_classifier_options= CONCEPT_CLASSIFIER_OPTIONS, 
			sentence_classifier_options= SENTENCE_CLASSIFIER_OPTIONS, 
			answer_summariser_options= SUMMARISER_OPTIONS, 
			# betweenness_centrality=None, 
		)
	qa.load_cache(qa_cache, save_if_init=True)
	if ADAPTIVE_QA:
		print('aspect_explainability_dict:', json.dumps(dict(sorted(qa.aspect_explainability_dict.items(), key=lambda x: x[-1], reverse=True)), indent=4))
	return qa, qa_cache

################ Define methods ################
# already_stored = False
def get_question_answer_dict(qa, question_list, options=None):
	if not options:
		options = {}
	return qa.ask(question_list, **options)

def get_question_answer_dict_quality(qa, question_answer_dict, top=5):
	return qa.get_question_answer_dict_quality(question_answer_dict, top=top)

def get_summarised_question_answer_dict(qa, question_answer_dict, options=None):
	if not options:
		options = {}
	return qa.summarise_question_answer_dict(question_answer_dict, **options)

def get_concept_overview(qa, query_template_list=None, concept_uri=None, concept_label= None, options=None, is_new_content_fn=None):
	if not options:
		options = {}
	question_answer_dict = qa.get_concept_overview(
		query_template_list= query_template_list, 
		concept_uri= concept_uri,
		concept_label= concept_label,
		adaptivity_options= ADAPTIVITY_OPTIONS,
		**options
	)
	# remove unanswered questions
	return dict(filter(lambda x: x[-1], question_answer_dict.items()))

def annotate_text(qa, sentence, similarity_threshold=None, max_concepts_per_alignment=1, tfidf_importance=None, is_preprocessed_content=True):
	return qa.concept_classifier.annotate(
		DocParser().set_content_list([sentence]), 
		similarity_threshold= similarity_threshold, 
		max_concepts_per_alignment= max_concepts_per_alignment,
		tfidf_importance= tfidf_importance,
		concept_id_filter= lambda x: x in qa.overview_aspect_set,
		is_preprocessed_content= is_preprocessed_content,
	)

def annotate_question_summary_tree(qa, question_summary_tree, similarity_threshold=None, max_concepts_per_alignment=1, tfidf_importance=None, is_preprocessed_content=True):
	return qa.annotate_question_summary_tree(question_summary_tree, similarity_threshold=similarity_threshold, max_concepts_per_alignment=max_concepts_per_alignment, tfidf_importance=tfidf_importance, is_preprocessed_content=is_preprocessed_content)

def get_taxonomical_view(qa, concept_uri, depth=0):
	return qa.get_taxonomical_view(concept_uri, depth=depth)

def annotate_taxonomical_view(qa, taxonomical_view, similarity_threshold=None, max_concepts_per_alignment=1, tfidf_importance=None, is_preprocessed_content=True):
	return qa.annotate_taxonomical_view(taxonomical_view, similarity_threshold=similarity_threshold, max_concepts_per_alignment=max_concepts_per_alignment, tfidf_importance=tfidf_importance, is_preprocessed_content=is_preprocessed_content)

def get_equivalent_concepts(qa, concept_uri):
	return qa.adjacency_list.get_equivalent_concepts(concept_uri)

def get_label_list(qa, concept_uri):
	return qa.kg_manager.get_label_list(concept_uri)

def store_cache(qa, qa_cache):
	qa.store_cache(qa_cache)

# ############### Cache scheduler ###############
# SCHEDULING_TIMER = 15*60 # 15 minutes
# from threading import Timer
# def my_task(is_first=False):
# 	if not is_first:
# 		store_cache()
# 	Timer(SCHEDULING_TIMER, my_task).start()
# # start your scheduler
# my_task(is_first=True)
