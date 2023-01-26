import sys

import json
import os

from knowpy.misc.doc_reader import DocParser
from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder as OB
from knowpy.models.classification.concept_classifier import ConceptClassifier
from knowpy.misc.doc_reader import load_or_create_cache
from knowpy.misc.graph_builder import get_concept_description_dict
from knowpy.misc.jsonld_lib import *

document_path = sys.argv[1]

text_list = [
	'Unless otherwise provided for in this Regulation, the law applicable to a noncontractual obligation arising out of a tort/delict shall be the law of the country in which the damage occurs irrespective of the country in which the event giving rise to the damage occurred and irrespective of the country or countries in which the indirect consequences of that event occur.',
	'The law applicable to a noncontractual obligation arising out of a restriction of competition shall be the law of the country where the market is, or is likely to be, affected.',
	'Article 18 Direct action against the insurer of the person liable The person having suffered damage may bring his or her claim directly against the insurer of the person liable to provide compensation if the law applicable to the noncontractual obligation or the law applicable to the insurance contract so provides.',
	'The law applicable to a noncontractual obligation arising out of an act of unfair competition shall be the law of the country where competitive relations or the collective interests of consumers are, or are likely to be, affected.',
	'The law applicable to a noncontractual obligation arising out of dealings prior to the conclusion of a contract, regardless of whether the contract was actually concluded or not, shall be the law that applies to the contract or that would have been applicable to it had it been entered into.',
	'The Commission, following the invitation by the European Parliament and the Council in the frame of Article 30 of the ‘Rome II’ Regulation, will submit, not later than December 2008, a study on the situation in the field of the law applicable to noncontractual obligations arising out of violations of privacy and rights relating to personality.'
]

################ Configuration ################

DEFAULT_OPTIONS = {
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

concept_classifier_cache = 'cache/QA_concept_classifier.pkl'
graph_cache = f"cache/OB_cache_lemma-{DEFAULT_OPTIONS['lemmatize_label']}.pkl"

################ Initialise data structures ################
print('Building Ontology Edge List..')
graph = load_or_create_cache(
	graph_cache, 
	lambda: OB(DEFAULT_OPTIONS).set_documents_path(document_path).build()
)
print('Ontology size:', len(graph))
print('Building Concept Classifier..')
graph_concept_description_dict = get_concept_description_dict(
	graph= graph, 
	label_predicate= HAS_LABEL_PREDICATE, 
	valid_concept_filter_fn= lambda x: '{obj}' in x[1]
)
ca = ConceptClassifier(DEFAULT_OPTIONS).set_concept_description_dict(graph_concept_description_dict)
ca.load_cache(concept_classifier_cache)

def align_doc_list(text_list, similarity_threshold=0.8, max_concepts_per_alignment=1):
	doc_parser = DocParser().set_content_list(text_list)
	return ca.align(doc_parser, similarity_threshold=similarity_threshold, max_concepts_per_alignment=max_concepts_per_alignment)

print(json.dumps(align_doc_list(text_list), indent=4))
