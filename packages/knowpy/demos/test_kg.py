import sys

from knowpy.models.knowledge_extraction.knowledge_graph_builder import KnowledgeGraphBuilder
import json

text_list = [
	# 'The Bank used an Artificial Neural Network as automated process to automatically decide whether to give a loan having many meanings.',
	# 'The Bank used an Artificial Neural Network as automated process to automatically decide whether to give a loan, then it adopted the Contrastive Explanations Method (CEM) algorithm to create the following explanation.',
	# 'She was unsure how her parents would react',
	# 'She was unsure',
	# 'He says that you and Maria like to swim',
	# 'The design of an algorithm has been allocating attention, bringing some normative questions into clear focus while obscuring others.',
	# 'The design of an algorithm allocates attention, bringing some normative questions into clear focus while obscuring others.',
	# 'Attention has been allocated to the design of an algorithm, bringing some normative questions into clear focus while obscuring others.',
	# 'She gave it to me.',
	# 'Which law applies to a non-contractual obligation?',
	# 'A consumer may bring proceedings against the other party to a contract either in the courts of the Member State in which that party is domiciled or, regardless of the domicile of the other party, in the courts for the place where the consumer is domiciled.',
	# "The law governing a contractual obligation under this Regulation shall apply to the extent that, in matters of contractual obligations, it contains rules which raise presumptions of law or determine the burden of proof.",
	# '(a) a contract for the sale of goods shall be governed by the law of the country where the seller has his habitual residence; (b) a contract for the provision of services shall be governed by the law of the country where the service provider has his habitual residence; (c) a contract relating to a right in rem in immovable property or to a tenancy of immovable property shall be governed by the law of the country where the property is situated; (d) notwithstanding point (c), a tenancy of immovable property concluded for temporary private use for a period of no more than six consecutive months shall be governed by the law of the country where the landlord has his habitual residence, provided that the tenant is a natural person and has his habitual residence in the same country; (e) a franchise contract shall be governed by the law of the country where the franchisee has his habitual residence; (f) a distribution contract shall be governed by the law of the country where the distributor has his habitual residence; (g) a contract for the sale of goods by auction shall be governed by the law of the country where the auction takes place, if such a place can be determined; (h) a contract concluded within a multilateral system which brings together or facilitates the bringing together of multiple third-party buying and selling interests in financial instruments, as defined by Article 4(1), point (17) of Directive 2004/39/EC, in accordance with non-discretionary rules and governed by a single law, shall be governed by that law.',
	# 'The law applicable to a non-contractual obligation arising out of dealings prior to the conclusion of a contract, regardless of whether the contract was actually concluded or not, shall be the law that applies to the contract or that would have been applicable to it had it been entered into.',
	# 'He said it to me',
	# 'The conflict-of-law rule in matters of product liability should meet the objectives of fairly spreading the risks inherent in a modern high-technology society, protecting consumers health, stimulating innovation, securing undistorted competition and facilitating trade.',
	# 'Which law is applied to a non-contractual obligation?',
	# 'To the design of an algorithm has been allocated attention, bringing some normative questions into clear focus while obscuring others.',
	# 'What automated process was used by the Bank to decide whether to give a loan?',
	# 'An Artificial Neural Network is used as automated process to automatically decide whether to give a loan.',
	# 'A Customer wants to know how and why the decision was made to accept or reject its loan application.',
	# 'If a noncontractual obligation arising out of unjust enrichment, including payment of amounts wrongly received, concerns a relationship existing between the parties, such as one arising out of a contract or a tort/delict.',
	# 'If a noncontractual obligation arising out of unjust enrichment, including payment of amounts wrongly received, concerns a relationship existing between the parties that is closely connected with that unjust enrichment, it shall be governed by the law that governs that relationship.',
	# 'If a noncontractual obligation arising out of unjust enrichment, including payment of amounts wrongly received, concerns a relationship existing between the parties, such as one arising out of a contract or a tort/delict, that is closely connected with that unjust enrichment, it shall be governed by the law that governs that relationship.',
	# 'In order to strike a reasonable balance between the parties, account must be taken, in so far as appropriate, of the rules of safety and conduct in operation in the country in which the harmful act was committed, even where the noncontractual obligation is governed by the law of another country.',
	# '(b) When the market is, or is likely to be, affected in more than one country, the person seeking compensation for damage who sues in the court of the domicile of the defendant, may instead choose to base his or her claim on the law of the court seised, provided that the market in that Member State is amongst those directly and substantially affected by the restriction of competition out of which the noncontractual obligation on which the claim is based arises; where the claimant sues, in accordance with the applicable rules on jurisdiction, more than one defendant in that court, he or she can only choose to base his or her claim on the law of that court if the restriction of competition on which the claim against each of these defendants relies directly and substantially affects also the market in the Member State of that court.',
	# 'When the market is, or is likely to be, affected in more than one country.',
	# 'He sends it and knows that and gives that to mario and maria.',
	'If Marco will go to the park, then he will be arrested.'
]

MAX_SINTAGMA_LENGTH = None
ADD_SUBCLASSES = False
USE_WORDNET = False
LEMMATIZE_LABEL = False
SIMILARITY_THRESHOLD = 0.6
DEFAULT_OPTIONS = {
	'similarity_threshold': 0.7,
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
	'with_centered_similarity': True,
}

kgb = KnowledgeGraphBuilder(DEFAULT_OPTIONS).set_content_list(text_list, remove_stopwords=False, remove_pronouns=False, remove_numbers=False)
edge_list = kgb.build(
	max_syntagma_length=MAX_SINTAGMA_LENGTH, 
	add_subclasses=ADD_SUBCLASSES, 
	use_wordnet=USE_WORDNET,
	lemmatize_label=LEMMATIZE_LABEL,
)
print('Triple count:', len(edge_list))
print(json.dumps(edge_list, indent=4))
