import sys

from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder
from knowpy.misc.doc_reader import load_or_create_cache

document_path = sys.argv[1]
result_path = sys.argv[2]

DEFAULT_OPTIONS = {
	# ontology builder stuff
	'max_syntagma_length': None,
	'lemmatize_label': False,
	
	'similarity_threshold': 0.8,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity': True,
}

ontology_edge_list = load_or_create_cache(
	f"cache/OB_cache_lemma-{DEFAULT_OPTIONS['lemmatize_label']}.pkl", 
	lambda: OntologyBuilder(DEFAULT_OPTIONS).set_documents_path(document_path).build()
)
print('Ontology size:', len(ontology_edge_list))
from knowpy.misc.graph_builder import save_graphml
save_graphml(ontology_edge_list, result_path+'ontology')
