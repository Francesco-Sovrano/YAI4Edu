import sys

from knowpy.misc.doc_reader import DocParser
from knowpy.models.classification.concept_classifier import ConceptClassifier
from knowpy.misc.onto_reader import get_concept_description_dict as get_ontology_concept_description_dict
import json

ontology_path = sys.argv[1]
document_path = sys.argv[2]
result_path = sys.argv[3]

SIMILARITY_THRESHOLD = 0.6
DEFAULT_OPTIONS = {
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity':True,
}

doc_parser = DocParser().set_documents_path(doc_path)
cc = ConceptClassifier(DEFAULT_OPTIONS).set_concept_description_dict(get_ontology_concept_description_dict(ontology_path))
concept_dict = cc.get_concept_dict(doc_parser, threshold=SIMILARITY_THRESHOLD, with_numbers=False)

missing_concepts_counter = cc.get_missing_concepts_counter(concept_dict)
document_concepts_related_to_ontology = set(concept_dict.keys()).difference(missing_concepts_counter.keys())
found_ontology_concept_set = set(
	ontology_concept['id']
	for concept in document_concepts_related_to_ontology
	for ontology_concept in concept_dict[concept]['similar_to']
)

possible_new_concepts = sorted(missing_concepts_counter.items(), key=lambda x: x[1], reverse=True)
possible_new_concepts = {key:value for key,value in possible_new_concepts if value > 1}

print('Concept dictionary:')
print(json.dumps(concept_dict, indent=4, sort_keys=True))
print('Possibly missing concepts:')
print(json.dumps(possible_new_concepts, indent=4))
print('Corpus concepts related to Ontology:', len(document_concepts_related_to_ontology))
print('Corpus concepts:', len(concept_dict))
print('Found Ontology Concepts:', len(found_ontology_concept_set))
print('Ontology Concepts:', len(ontology_concept_description_dict))


from wordcloud import WordCloud
import matplotlib.pyplot as plt
 
# Create the wordcloud object
wordcloud = WordCloud(width=900,height=500, relative_scaling=1, normalize_plurals=True).generate_from_frequencies(possible_new_concepts)
 
# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.savefig(result_path)
