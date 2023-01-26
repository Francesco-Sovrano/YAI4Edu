import sys

from knowpy.models.classification.concept_classifier import ConceptClassifier
from knowpy.models.knowledge_extraction.knowledge_graph_builder import KnowledgeGraphBuilder
import itertools
from more_itertools import unique_everseen
from nltk.corpus import wordnet as wn
from pywsd import disambiguate
from pywsd.lesk import cosine_lesk
import numpy as np
import random

#text = 'In summary, the open nature of the Internet as a transaction infrastructure and its global nature create uncertainty around on-line transactions, and this poses trust, credibility and risk as crucial elements of e-transaction (Hoffman et al., 1999).'
#text = 'The idea of having a cascade of mix servers was expanded in [28] which proposed onion routing mechanisms that became the de facto privacy preserving protocols.'
#text = 'For the purposes of this Regulation, references to rights and obligations constituting the terms and conditions governing the issuance, offers to the public or public take-over bids of transferable securities and references to the subscription and redemption of units in collective investment undertakings should include the terms governing, inter alia, the allocation of securities or units, rights in the event of over-subscription, withdrawal rights and similar matters in the context of the offer as well as those matters referred to in Articles 10, 11, 12 and 13, thus ensuring that all relevant contractual aspects of an offer binding the issuer or the offeror to the consumer are governed by a single law.'
#text = "The question of when the person seeking compensation can make the choice of the law applicable should be determined in accordance with the law of the Member State in which the court is seised."
#text = "Where establishing the existence of the agreement, the court has to respect the intentions of the parties."
#text = 'Mario was sent by Giulio. Giulio sent Mario.'
#text = 'Mario and Giulio were sent by the department, and they said that it was incredible.'
text = 'He poured orange juice on his cereal.'
#text = 'A rare black squirrel has become a regular visitor to a suburban garden.'
#text = 'President Obama gave a speech at New Jersey to thousands of people.'

SIMILARITY_THRESHOLD = 0.6
ADD_SUBCLASSES = False
USE_FRAMENET_FE = False
MIN_EDGE_FREQUENCY = 1
MIN_CONCEPT_FREQUENCY = 1
MAX_SYNTAGMA_LENGTH = 5
DEFAULT_OPTIONS = {
	'similarity_threshold': 0.7,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity': True,
}

def get_synset_description_list(synset_list):
	return {
		synset.name().strip(): [
			lemma.name().strip().replace('_',' ') 
			for lemma in synset.lemmas()
		]
		for synset in synset_list
	}

def get_lemma_synsets(lemma, pos=None):
	return wn.synsets(lemma.replace(' ','_'), pos=pos)

def find_related_terms(lemma, min_size, pos=None):
	lemma_synsets = get_lemma_synsets(lemma, pos)
	lemma_synsets = filter(lambda x:lemma.replace(' ','_') in map(lambda y:y.name(), x.lemmas()), lemma_synsets)
	lemma_synsets = set(lemma_synsets)
	if len(lemma_synsets) == 0:
		return []
	related_terms = []
	hyper_depth = 1
	while len(related_terms) < min_size:
		for synset in lemma_synsets:
			hypo = lambda x: (h for h in x.hyponyms() if h not in lemma_synsets)
			for hypernym in synset.closure(lambda x: x.hypernyms(),hyper_depth):
				hypernyms = hypernym.closure(hypo)
				hypernyms = filter(lambda h: sum(1 if len(hh.hyponyms())==0 else 0 for hh in h.hyponyms())==len(h.hyponyms()), hypernyms)
				related_terms += hypernyms
		hyper_depth += 1
		related_terms = list(unique_everseen(related_terms, key=lambda x: x.hypernyms()))
	#related_terms = related_terms[:min_size]
	related_terms = random.sample(related_terms, min_size)
	related_terms.extend(lemma_synsets)
	return related_terms

def get_contextualized_alternative_terms(lemma, context, threshold=None, size=None, desc=True):
	related_terms = find_related_terms(lemma, pos=wn.NOUN, min_size=2**7)
	if len(related_terms) == 0:
		return []
	model = ConceptClassifier(DEFAULT_OPTIONS).set_concept_description_dict(get_synset_description_list(related_terms))
	subj_similarity = model.get_query_similarity(context)
	subj_contextualized_alternatives_iter = model.get_index_of_most_similar_documents(subj_similarity['weighted'], threshold=threshold, desc=desc)
	subj_contextualized_alternatives_iter = unique_everseen(subj_contextualized_alternatives_iter, key=lambda x: x['doc'])
	subj_contextualized_alternatives_iter = itertools.islice(subj_contextualized_alternatives_iter, size)
	return subj_contextualized_alternatives_iter

# Cache wordnet
# ConceptClassifier(DEFAULT_OPTIONS).set_concept_description_dict(get_synset_description_list(wn.all_synsets('n')))

kgb = KnowledgeGraphBuilder(DEFAULT_OPTIONS).set_content_list([text], remove_pronouns=False)
edge_list = []
'''
edge_list = kgb.build(
	max_syntagma_length=MAX_SYNTAGMA_LENGTH, 
	min_edge_frequency=MIN_EDGE_FREQUENCY, 
	min_concept_frequency=MIN_CONCEPT_FREQUENCY, 
	add_subclasses=ADD_SUBCLASSES, 
	use_framenet_fe=USE_FRAMENET_FE
)
'''

print('Triple count:', len(edge_list))
'''
	('he', 'poured', 'orange juice on his cereal'),
	('he', 'poured', 'juice on his cereal'),
	('he', 'poured', 'milk on his cereal'),
	('he', 'put', 'an elephant into the fridge'),
	('he', 'put', 'a chicken into the fridge'),
	('my sister', 'eats', 'a stone after breakfast every day'),
	('my sister', 'eats', 'an apple after breakfast every day'),
	('money', 'can be used for', 'buying stars'),
	('money', 'can be used for', 'buying tickets'),
	('money', 'can be used for', 'buying fireworks'),
	('money', 'can be used for', 'buying the sun'),

	('orange juice', 'is poured on', 'his cereal'),
	('juice', 'is poured on', 'his cereal'),
	('milk', 'is poured on', 'his cereal'),
	('an elephant', 'is put into', 'fridge'),
	('a turkey', 'is put into', 'fridge'),
	('a chicken', 'is put into', 'fridge'),
	('my sister', 'eats', 'a stone'),
	('my sister', 'eats', 'an apple'),
	('money', 'can be used for', 'buying stars'),
	('money', 'can be used for', 'buying tickets'),
	('money', 'can be used for', 'buying fireworks'),
	('money', 'can be used for', 'buying the sun'),

	('orange juice', 'pour on', 'cereal'),
	('juice', 'pour on', 'cereal'),
	('milk', 'pour on', 'cereal'),
	('elephant', 'put into', 'fridge'),
	('turkey', 'put into', 'fridge'),
	('chicken', 'put into', 'fridge'),
	('sister', 'eat', 'stone'),
	('sister', 'eat', 'apple'),
	('money', 'use for', 'buying star'),
	('money', 'use for', 'buying ticket'),
	('money', 'use for', 'buying firework'),
	('money', 'use for', 'buying sun'),

	('orange juice', 'pour on', 'cereal'),
	('juice', 'pour on', 'cereal'),
	('milk', 'pour on', 'cereal'),
	('elephant', 'put into', 'fridge'),
	('turkey', 'put into', 'fridge'),
	('chicken', 'put into', 'fridge'),
	('sister', 'eat', 'stone'),
	('sister', 'eat', 'apple'),
	('money', 'use for', 'star'),
	('money', 'use for', 'ticket'),
	('money', 'use for', 'firework'),
	('money', 'use for', 'sun'),
'''
edge_list = [
	('orange juice', 'pour on', 'cereal'),
	('juice', 'pour on', 'cereal'),
	('milk', 'pour on', 'cereal'),
	('elephant', 'put into', 'fridge'),
	('turkey', 'put into', 'fridge'),
	('chicken', 'put into', 'fridge'),
	('sister', 'eat', 'stone'),
	('sister', 'eat', 'apple'),
	('money', 'use for', 'star'),
	('money', 'use for', 'ticket'),
	('money', 'use for', 'firework'),
	('money', 'use for', 'sun'),
]

cedge_list = [
	('orange juice is poured on', 'is poured on his cereal'),
	('juice is poured on', 'is poured on his cereal'),
	('milk is poured on', 'is poured on his cereal'),
	('an elephant is put into', 'is put into fridge'),
	('a turkey is put into', 'is put into fridge'),
	('a chicken is put into', 'is put into fridge'),
	('my sister eats', 'eats a stone'),
	('my sister eats', 'eats an apple'),
	('money can be used for', 'can be used for stars'),
	('money can be used for', 'can be used for tickets'),
	('money can be used for', 'can be used for fireworks'),
	('money can be used for', 'can be used for the sun'),
]
'''
cedge_list = [
	('he poured orange juice on', 'he poured on his cereal'),
	('he poured juice on', 'he poured on his cereal'),
	('he poured milk on', 'he poured on his cereal'),
	('he put an elephant into', 'he put into fridge'),
	('he put turkey into', 'he put into fridge'),
	('he put chicken into', 'he put into fridge'),
	('my sister eats', 'eats a stone'),
	('my sister eats', 'eats an apple'),
	('money can be used for', 'can be used for stars'),
	('money can be used for', 'can be used for tickets'),
	('money can be used for', 'can be used for fireworks'),
	('money can be used for', 'can be used for the sun'),
]
'''
sentencify = lambda x: ' '.join(x)+'.'
for edge,cedge in zip(edge_list,cedge_list):
	#edge_str = sentencify(edge)
	#hidden_subj_edge_str = sentencify(('x',)+edge[1:])
	#hidden_obj_edge_str = sentencify(edge[:-1]+('x',))
	#sim = kgb.couple_extractor.get_similarity_vector(source_text=edge_str, target_text_list=[hidden_subj_edge_str,], cached=False)
	print('#', sentencify(edge))
	
	subj,pred,obj = edge
	#lemmatized_edge = list(map(lambda x: x.replace(' ','_') ,edge))
	#print(disambiguate(sentencify(edge), algorithm=cosine_lesk))
	'''
	edge_synsets = [
		synset
		for token,synset in disambiguate(sentencify((subj.replace(' ','-'),pred,obj.replace(' ','-'))), algorithm=cosine_lesk)
		if token in edge
	]
	subj_synsets = [edge_synsets[0].name() if edge_synsets[0] is not None else '']
	obj_synsets = [edge_synsets[-1].name() if edge_synsets[-1] is not None else '']

	subj_synsets = set(map(lambda x: x.name(),get_lemma_synsets(subj, wn.NOUN)))
	obj_synsets = set(map(lambda x: x.name(),get_lemma_synsets(obj, wn.NOUN)))
	
	subj_synsets = [get_lemma_synsets(subj, wn.NOUN)[0].name()]
	obj_synsets = [get_lemma_synsets(obj, wn.NOUN)[0].name()]
	'''

	def clean(similarity_list):
		mean = np.mean(similarity_list)
		std = np.std(similarity_list)
		return list(filter(lambda x: abs((x-mean)/std) <= 1, similarity_list))

	subj_contextualized_alternatives_iter = get_contextualized_alternative_terms(lemma=subj, context=cedge[1])
	subj_contextualized_alternatives_list = list(subj_contextualized_alternatives_iter)
	#print(subj_contextualized_alternatives_list[:10])
	#subj_contextualized_alternatives_list = subj_contextualized_alternatives_list[:len(subj_contextualized_alternatives_list)//2]
	subj_similarity_list = list(map(lambda x: x['similarity'], subj_contextualized_alternatives_list))
	#subj_similarity_list = clean(subj_similarity_list)
	#subj_similarity_list = clean(subj_similarity_list)
	subj_mean = np.mean(subj_similarity_list)
	subj_std = np.std(subj_similarity_list)

	subj_similarity_dict = next(filter(lambda x: x['doc'] == subj, subj_contextualized_alternatives_list), None)
	if subj_similarity_dict is not None:
		norm_subj_sim = (subj_similarity_dict['similarity']-subj_mean)/subj_std
		print(subj_similarity_dict['doc'], norm_subj_sim, subj_similarity_dict['similarity'])
	else:
		norm_subj_sim = -1

	obj_contextualized_alternatives_iter = get_contextualized_alternative_terms(lemma=obj, context=cedge[0])
	obj_contextualized_alternatives_list = list(obj_contextualized_alternatives_iter)
	#obj_contextualized_alternatives_list = obj_contextualized_alternatives_list[:len(obj_contextualized_alternatives_list)//2]
	obj_similarity_list = list(map(lambda x: x['similarity'], obj_contextualized_alternatives_list))
	#obj_similarity_list = clean(obj_similarity_list)
	#obj_similarity_list = clean(obj_similarity_list)
	obj_mean = np.mean(obj_similarity_list)
	obj_std = np.std(obj_similarity_list)
	obj_similarity_dict = next(filter(lambda x: x['doc'] == obj, obj_contextualized_alternatives_list), None)
	if obj_similarity_dict is not None:
		norm_obj_sim = (obj_similarity_dict['similarity']-obj_mean)/obj_std
		print(obj_similarity_dict['doc'], norm_obj_sim, obj_similarity_dict['similarity'])
	else:
		norm_obj_sim = -1

	print((norm_obj_sim+norm_subj_sim)/2)

#from misc.graph_builder import save_graph
#save_graph(edge_list, result_path, max(min(256,len(edge_list)/2),32))
