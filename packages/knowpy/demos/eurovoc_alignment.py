import sys

from knowpy.misc.doc_reader import DocParser
from knowpy.models.classification.eurovoc_classifier import EuroVocClassifier
import json

document_path = sys.argv[1]
result_path = sys.argv[2]

doc_parser = DocParser().set_documents_path(document_path)
concept_dict = EuroVocClassifier().get_concept_dict(doc_parser)

missing_concepts_counter = EuroVocClassifier.get_missing_concepts_counter(concept_dict)
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


from wordcloud import WordCloud
import matplotlib.pyplot as plt
 
# Create the wordcloud object
wordcloud = WordCloud(width=900,height=500, relative_scaling=1, normalize_plurals=True).generate_from_frequencies(possible_new_concepts)
 
# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.savefig(result_path)
