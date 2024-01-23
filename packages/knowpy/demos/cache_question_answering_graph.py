import numpy as np
import json
import sys

from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder as OB
from knowpy.models.reasoning.question_answerer import QuestionAnswerer

from knowpy.misc.doc_reader import load_or_create_cache
from knowpy.misc.graph_builder import save_graphml

document_path = sys.argv[1]
# result_path = sys.argv[2]

QA_DEFAULT_OPTIONS = {
	'log': True,
}

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
	'default_tfidf_importance': 0,
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
	'default_tfidf_importance': 0,
}

SUMMARISER_DEFAULT_OPTIONS = {
	'hf_model': {
		# 'url': 't5-small',
		'url': 'facebook/bart-large-cnn', # baseline
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

ontology_edge_list = load_or_create_cache(
	ontology_edge_list_cache, 
	lambda: OB(ONTOLOGY_BUILDER_DEFAULT_OPTIONS).set_documents_path(document_path).build()
)

print('Ontology size:', len(ontology_edge_list))
# save_graphml(ontology_edge_list, result_path+'ontology')

qa = QuestionAnswerer(
	graph= ontology_edge_list, 
	model_options= QA_DEFAULT_OPTIONS,
	query_concept_classifier_options= CONCEPT_CLASSIFIER_DEFAULT_OPTIONS, 
	answer_classifier_options= SENTENCE_CLASSIFIER_DEFAULT_OPTIONS, 
	answer_summariser_options= SUMMARISER_DEFAULT_OPTIONS,
)
qa.cache_whole_graph(sentence_classifier_cache, concept_classifier_cache, sentence_summariser_cache)
