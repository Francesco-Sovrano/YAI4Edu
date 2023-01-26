import sys

from knowpy.misc.doc_reader import DocParser
from knowpy.models.knowledge_extraction.couple_extractor import CoupleExtractor
from knowpy.models.knowledge_extraction.couple_abstractor import WordnetAbstractor

DEFAULT_OPTIONS = {
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'lu_confidence_threshold': 2/3,
	'concept_confidence_threshold': 1/2,
}

#text = 'In summary, the open nature of the Internet as a transaction infrastructure and its global nature create uncertainty around on-line transactions, and this poses trust, credibility and risk as crucial elements of e-transaction (Hoffman et al., 1999).'
#text = 'The idea of having a cascade of mix servers was expanded in [28] which proposed onion routing mechanisms that became the de facto privacy preserving protocols.'
#text = 'For the purposes of this Regulation, references to rights and obligations constituting the terms and conditions governing the issuance, offers to the public or public take-over bids of transferable securities and references to the subscription and redemption of units in collective investment undertakings should include the terms governing, inter alia, the allocation of securities or units, rights in the event of over-subscription, withdrawal rights and similar matters in the context of the offer as well as those matters referred to in Articles 10, 11, 12 and 13, thus ensuring that all relevant contractual aspects of an offer binding the issuer or the offeror to the consumer are governed by a single law.'
#text = "The question of when the person seeking compensation can make the choice of the law applicable should be determined in accordance with the law of the Member State in which the court is seised."
#text = "Where establishing the existence of the agreement, the court has to respect the intentions of the parties."
#text = 'Mario was sent by Giulio. Giulio sent Mario.'
#text = 'Mario and Giulio were sent by the department, and they said that it was incredible.'
#text = 'He poured orange juice on his cereal and the glass.'
#text = 'A rare black squirrel has become a regular visitor to a suburban garden.'
#text = 'President Obama gave a speech at New Jersey to thousands of people.'
text = 'money can be used for buying stars'

doc_parser = DocParser().set_content_list([text])
couple_list = CoupleExtractor(DEFAULT_OPTIONS).get_couple_list(doc_parser)
couple_list = WordnetAbstractor(DEFAULT_OPTIONS).abstract_couple_list(couple_list)

print('Sentence:', text)
print('Patterns:')
for couple in couple_list:
	
	if 'obj' in couple['dependency']:
		print(couple['composite_predicate_core']['lemma'], couple['concept']['lemma'])
	else:
		print(couple['concept']['lemma'], couple['composite_predicate_core']['lemma'])
	