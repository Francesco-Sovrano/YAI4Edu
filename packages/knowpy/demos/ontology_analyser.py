import sys

import json
from knowpy.models.knowledge_extraction.ontology_builder import OntologyBuilder
from knowpy.misc.doc_reader import load_or_create_cache

from nltk import FreqDist
from nltk.corpus import brown
frequency_distribution = FreqDist(i.lower() for i in brown.words())
# frequency_distribution.most_common()[:10]

document_path = sys.argv[1]
result_path = sys.argv[2]

DEFAULT_OPTIONS = {
	# ontology builder stuff
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

ontology_edge_list = load_or_create_cache(
	f"cache/OB_cache_lemma-{DEFAULT_OPTIONS['lemmatize_label']}.pkl", 
	lambda: OntologyBuilder(DEFAULT_OPTIONS).set_documents_path(document_path).build()
)
print('Ontology size:', len(ontology_edge_list))
from misc.graph_builder import save_graphml
save_graphml(ontology_edge_list, result_path+'ontology')

import networkx as nx

G = nx.Graph()
DiG = nx.DiGraph()
for s,p,o in ontology_edge_list:
	if '{obj}' not in p:
		continue
	DiG.add_edge(s,o)
	G.add_edge(s,o)
h, a = nx.hits(DiG)
print('frequency',json.dumps(dict(sorted(((k,frequency_distribution.freq(k[3:])) for k in h.keys()), key=lambda x:x[-1], reverse=True)), indent=4))
print('hubs',json.dumps(dict(sorted(h.items(), key=lambda x:x[-1], reverse=True)), indent=4))
print('authorities',json.dumps(dict(sorted(a.items(), key=lambda x:x[-1], reverse=True)), indent=4))

print('pagerank',json.dumps(dict(sorted(nx.pagerank(DiG).items(), key=lambda x:x[-1], reverse=True)), indent=4))

# print('closeness_vitality', nx.closeness_vitality(DiG))
# print('maximal_independent_set', nx.maximal_independent_set(G))

# from networkx.algorithms import approximation
# print('treewidth_min_degree', approximation.treewidth_min_degree(G))

# print('immediate_dominators', ontology_edge_list[0][0],  json.dumps(nx.immediate_dominators(DiG, ontology_edge_list[0][0]), indent=4))

# print('percolation_centrality',json.dumps(dict(sorted(nx.percolation_centrality(DiG).items(), key=lambda x:x[-1], reverse=True)), indent=4))
print('closeness_centrality',json.dumps(dict(sorted(nx.closeness_centrality(DiG).items(), key=lambda x:x[-1], reverse=True)), indent=4))
print('betweenness_centrality',json.dumps(dict(sorted(nx.betweenness_centrality(DiG).items(), key=lambda x:x[-1], reverse=True)), indent=4))
# print('edge_betweenness_centrality',json.dumps(dict(sorted(nx.edge_betweenness_centrality(DiG).items(), key=lambda x:x[-1], reverse=True)), indent=4))
print('eigenvector_centrality',json.dumps(dict(sorted(nx.eigenvector_centrality(DiG).items(), key=lambda x:x[-1], reverse=True)), indent=4))
