import sys

from knowpy.models.knowledge_extraction.knowledge_graph_builder import KnowledgeGraphBuilder
from knowpy.misc.graph_builder import get_biggest_connected_graph
from knowpy.misc.onto_reader import get_concept_description_dict as get_ontology_concept_description_dict

ontology_path = sys.argv[1]
document_path = sys.argv[2]
result_path = sys.argv[3]

SIMILARITY_THRESHOLD = 0.6
ADD_SUBCLASSES = False
USE_FRAMENET_FE = False
MIN_EDGE_FREQUENCY = 3
MIN_CONCEPT_FREQUENCY = 1
MAX_SYNTAGMA_LENGTH = 5
DEFAULT_OPTIONS = {
	'lu_confidence_threshold': 3/4,
	'concept_confidence_threshold': 3/4,

	'similarity_threshold': 0.7,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity': True,
}

kgb = KnowledgeGraphBuilder(DEFAULT_OPTIONS).set_documents_path(document_path)
kgb.set_concept_filter(concept_description_dict=get_ontology_concept_description_dict(ontology_path), similarity_threshold=SIMILARITY_THRESHOLD, cache_file='kgb.pkl')
edge_list = kgb.build(
	max_syntagma_length=MAX_SYNTAGMA_LENGTH, 
	min_edge_frequency=MIN_EDGE_FREQUENCY, 
	min_concept_frequency=MIN_CONCEPT_FREQUENCY, 
	add_subclasses=ADD_SUBCLASSES, 
	use_framenet_fe=USE_FRAMENET_FE
)
edge_list = get_biggest_connected_graph(edge_list)

print('Triple count:', len(edge_list))

from misc.graph_builder import save_graph
save_graph(edge_list, result_path, max(min(256,len(edge_list)/2),32))
