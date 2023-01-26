import json
import sys

from knowpy.models.knowledge_extraction import OntologyBuilder as OB
from knowpy.models.reasoning import QuestionAnswerer
from knowpy.misc import load_or_create_cache
from knowpy.misc import save_graphml
import itertools

document_path = sys.argv[1]
# result_path = sys.argv[2]

concept_uri_list = (
	"my:obligation",
	# "my:contractual_obligation",
	# "my:noncontractual_obligation",
)

query_template_list = [
	##### Expository
	# 'How?',
	##### Quantitative
	# 'How much?',
	##### Causal + Justificatory
	'Why?',
	##### Theleological
	'What for?',
	##### Descriptive
	'What?',
	# 'Who?',
	##### Temporal
	# 'When?',
	##### Spatial
	# 'Where?',
	##### Directional
	# 'Where to?',
	##### Unknown
	# 'Who by?',
	# 'Why not?',
	# 'Whose?',
	# 'What if?',
]

get_concept_overview_options = {
	'answer_pertinence_threshold': 0.02, 
	'add_external_definitions': True, 
	'add_clustered_triples': False, 
	'include_super_concepts_graph': False, 
	'include_sub_concepts_graph': True, 
	'consider_incoming_relations': True,
}

summarise_question_answer_dict_options = {
	'ignore_non_grounded_answers': False, 
	'use_abstracts': False, 
	'summary_horizon': 20,
	'tree_arity': 20, 
	# 'cut_factor': 2, 
	# 'depth': 1,
	'remove_duplicates': True,
}

QA_DEFAULT_OPTIONS = {'log': False}

ONTOLOGY_BUILDER_DEFAULT_OPTIONS = {
	'max_syntagma_length': None,
	'lemmatize_label': False,

	'similarity_threshold': 0.7,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity': True,
}

CONCEPT_CLASSIFIER_DEFAULT_OPTIONS = {
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity': True,
}

SENTENCE_CLASSIFIER_DEFAULT_OPTIONS = {
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-qa/3', # English QA
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3', # Multilingual QA # 16 languages (Arabic, Chinese-simplified, Chinese-traditional, English, French, German, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Spanish, Thai, Turkish, Russian)
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	}, 
	'with_centered_similarity': False,
	'with_topic_scaling': False,
	'with_stemmed_tfidf': False,
}

SUMMARISER_DEFAULT_OPTIONS = {
	'hf_model': {
		'url': 't5-small',
		# 'url': 'facebook/bart-large-cnn', # baseline
		# 'url': 'sshleifer/distilbart-cnn-12-6', # speedup (over the baseline): 1.24
		# 'url': 'sshleifer/distilbart-cnn-12-3', # speedup (over the baseline): 1.78
		# 'url': 'sshleifer/distilbart-cnn-6-6', # speedup (over the baseline): 2.09
		'framework': 'pt',
		'type': 'summarization',
		'cache_dir': '/Users/toor/Documents/Software/DLModels/hf_cache_dir/',
	},
}

ontology_edge_list_cache = f"cache/OB_cache_lemma-{ONTOLOGY_BUILDER_DEFAULT_OPTIONS['lemmatize_label']}.pkl"
concept_classifier_cache = 'cache/QA_concept_classifier.pkl'
sentence_classifier_cache = 'cache/QA_sentence_classifier.pkl'
sentence_summariser_cache = 'cache/QA_sentence_summariser.pkl'

process_name = "this regulation"
# query_list = [
# 	"What is {concept}, in {process}?", # Descriptive
# 	"What is the purpose of {concept}, in {process}?", # Teleological
# 	"What justifies {concept}, according to {process}?", # Justificatory
# 	"What could {concept} cause, according to {process}?", # Causal
# 	"What causes {concept}, according to {process}?", # Causal
# ]
# query_list = [
# 	"What is the role of {concept} in the underlying mechanisms of {process}?",
#	 "What is the role of {concept} in the data used to create {process}?",
#	 "What is the role of {concept} in the context of {process}?",
#	 "What are the possible consequences of {process} with respect to {concept}?",
#	 "What is the role of {concept} in justifying {process}?",
#	 "Why is {concept} mentioned in {process}?",
# ]

ontology_edge_list = load_or_create_cache(
	ontology_edge_list_cache, 
	lambda: OB(ONTOLOGY_BUILDER_DEFAULT_OPTIONS).set_documents_path(document_path).build()
)

print('Ontology size:', len(ontology_edge_list))
# save_graphml(ontology_edge_list, result_path+'ontology')

print('Questions:', query_template_list)
qa = QuestionAnswerer(
	graph= ontology_edge_list, 
	model_options= QA_DEFAULT_OPTIONS,
	query_concept_classifier_options= CONCEPT_CLASSIFIER_DEFAULT_OPTIONS, 
	answer_classifier_options= SENTENCE_CLASSIFIER_DEFAULT_OPTIONS, 
	answer_summariser_options= SUMMARISER_DEFAULT_OPTIONS,
)
qa.sentence_classifier.load_cache(sentence_classifier_cache)
qa.concept_classifier.load_cache(concept_classifier_cache)
qa.sentence_summariser.load_cache(sentence_summariser_cache)
##########################################
for concept_uri in concept_uri_list:
	question_answer_dict = qa.get_concept_overview(
		query_template_list, 
		concept_uri,
		**get_concept_overview_options
	)
	question_summary_tree = qa.summarise_question_answer_dict(
		question_answer_dict, 
		**summarise_question_answer_dict_options
	)
	result = {
		'question_summary_tree': question_summary_tree,
		'annotation_dict': qa.annotate_question_summary_tree(question_summary_tree),
		'taxonomical_view': qa.get_taxonomical_view(concept_uri, depth=0)
	}
	print(concept_uri, json.dumps(result, indent=4))
##########################################
# qa.sentence_summariser.store_cache(sentence_summariser_cache)
# qa.concept_classifier.store_cache(concept_classifier_cache)
# qa.sentence_classifier.store_cache(sentence_classifier_cache)
