import numpy as np
import json
import sys

from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder as OB
from knowpy.models.reasoning.question_answerer import QuestionAnswerer

from knowpy.misc.doc_reader import load_or_create_cache
from knowpy.misc.graph_builder import save_graphml

document_path = sys.argv[1]
# result_path = sys.argv[2]

ask_options = {
	'answer_pertinence_threshold': 0.3, 
	'keep_the_n_most_similar_concepts': 1, 
	'query_concept_similarity_threshold': 0.55, 
	'add_external_definitions': False, 
	'add_clustered_triples': False
}
summarise_question_answer_dict_options = {
	'ignore_non_grounded_answers': True, 
	'use_abstracts': False, 
	'summary_horizon': 20,
	'tree_arity': 5, 
	'cut_factor': 2, 
	'depth': 1
}

question_list = [
	# 'What is an obligation?',
	# 'What is the purpose of an obligation?',
	# "What could cause an obligation?", 
	# "What may justify an obligation?",
	# 'What is a non-contractual obligation?',
	# 'What is the purpose of a non-contractual obligation?',
	# "What could cause a non-contractual obligation?", 
	# "What may justify a non-contractual obligation?",
	# 'What is a contractual obligation?',
	# 'What is the purpose of a contractual obligation?',
	# "What could cause a contractual obligation?", 
	# "What may justify a contractual obligation?",
	# 'What does apply to a contract?',
	# 'When does a contract conclude?',
	# 'What is governed by a contract?',
	"Which law is applicable to a contractual obligation?",
	"In which court is celebrated the trial in case the consumer is domiciled in a Member State?",
	"In which court is celebrated the trial in case the employer is domiciled in a Member State?",
]

QA_DEFAULT_OPTIONS = {
	'log': False,
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
	'default_tfidf_importance': 1/5,
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
		'url': 't5-small',
		# 'url': 'facebook/bart-large-cnn', # baseline
		# 'url': 'sshleifer/distilbart-cnn-12-6', # speedup (over the baseline): 1.24
		# 'url': 'sshleifer/distilbart-cnn-12-3', # speedup (over the baseline): 1.78
		# 'url': 'sshleifer/distilbart-cnn-6-6', # speedup (over the baseline): 2.09
		'cache_dir': '/Users/toor/Documents/Software/DLModels/hf_cache_dir/',
		'framework': 'pt',
		'type': 'summarization',
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
qa.sentence_classifier.load_cache(sentence_classifier_cache)
qa.concept_classifier.load_cache(concept_classifier_cache)
qa.sentence_summariser.load_cache(sentence_summariser_cache)
# question_answer_dict = load_or_create_cache(
# 	f"question_answer_dict.pkl", 
# 	lambda: qa.ask(
# 		question_list, 
# 		**ask_options
# 	)
# )
question_answer_dict = qa.ask(
	question_list, 
	**ask_options
)
# print('######## Question Answers ########')
# print(json.dumps(question_answer_dict, indent=4))
# print('#'*100)

question_summarised_answer_dict = qa.summarise_question_answer_dict(question_answer_dict, **summarise_question_answer_dict_options)
print('######## Summarised Question Answers ########')
print(json.dumps(question_summarised_answer_dict, indent=4))
qa.sentence_summariser.store_cache(sentence_summariser_cache)
qa.concept_classifier.store_cache(concept_classifier_cache)
qa.sentence_classifier.store_cache(sentence_classifier_cache)
