import numpy as np
import json
import sys

from knowpy.models.summarisation.neural_sentence_summariser import NeuralSentenceSummariser

SUMMARISER_DEFAULT_OPTIONS = {
	# 'summary_model': 'facebook/bart-large-cnn', # baseline
	# 'summary_model': 'sshleifer/distilbart-cnn-12-6', # speedup (over the baseline): 1.24
	# 'summary_model': 'sshleifer/distilbart-cnn-12-3', # speedup (over the baseline): 1.78
	# 'summary_model': 'sshleifer/distilbart-cnn-6-6', # speedup (over the baseline): 2.09
	'summary_model': 't5-small',
	'framework': 'pt',
	'cache_dir': '/Users/toor/Documents/University/PhD/Paper/Literature/NLP/Papers/Multi-Sentence Compression/[2019]Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer/models/',
}

answer_list = [ # sentences
	"Unless otherwise provided for in this Regulation, the law applicable to a noncontractual obligation arising out of a tort/delict shall be the law of the country in which the damage occurs irrespective of the country in which the event giving rise to the damage occurred and irrespective of the country or countries in which the indirect consequences of that event occur.",
	"Formal validity A unilateral act intended to have legal effect and relating to a noncontractual obligation shall be formally valid if it satisfies the formal requirements of the law governing the noncontractual obligation in question or the law of the country in which the act is performed.",
	"The Commission will make a proposal to the European Parliament and the Council concerning the procedures and conditions according to which Member States would be entitled to negotiate and conclude on their own behalf agreements with third countries in individual and exceptional cases, concerning sectoral matters, containing provisions on the law applicable to noncontractual obligations.",
	"the law applicable to a noncontractual obligation is the law applicable",
	"The law applicable to such noncontractual obligations should be the law of the country where the market is, or is likely to be, affected.",
	"The following shall be excluded from the scope of this Regulation: (a) noncontractual obligations arising out of family relationships and relationships deemed by the law applicable to such relationships to have comparable effects including maintenance obligations; (b) noncontractual obligations arising out of matrimonial property regimes, property regimes of relationships deemed by the law applicable to such relationships to have comparable effects to marriage, and wills and succession; (c) noncontractual obligations arising under bills of exchange, cheques and promissory notes and other negotiable instruments to the extent that the obligations under such other negotiable instruments arise out of their negotiable character; (d) noncontractual obligations arising out of the law of companies and other bodies corporate or unincorporated regarding matters such as the creation, by registration or otherwise, legal capacity, internal organisation or windingup of companies and other bodies corporate or unincorporated, the personal liability of officers and members as such for the obligations of the company or body and the personal liability of auditors to a company or to its members in the statutory audits of accounting documents; (e)",
	"mandatory provisions Nothing in this Regulation shall restrict the application of the provisions of the law of the forum in a situation where they are mandatory irrespective of the law otherwise applicable to the noncontractual obligation.",
	"(31) To respect the principle of party autonomy and to enhance legal certainty, the parties should be allowed to make a choice as to the law applicable to a noncontractual obligation.",
	"The Commission will make a proposal to the European Parliament and to the Council concerning the procedures and conditions according to which Member States would be entitled to negotiate and conclude, on their own behalf, agreements with third countries in individual and exceptional cases, concerning sectoral matters and containing provisions on the law applicable to contractual obligations.",
	"Effect may be given to the overriding mandatory provisions of the law of the country where the obligations arising out of the contract have to be or have been performed, in so far as those overriding mandatory provisions render the performance of the contract unlawful.",
	"V COMMON RULES Article 15 Scope of the law applicable The law applicable to noncontractual obligations under this Regulation shall govern in particular: (a)",
	"This Regulation shall not prejudice the application of international conventions to which one or more Member States are parties at the time when this Regulation is adopted and which lay down conflictoflaw rules relating to noncontractual obligations.",
	"the law applicable to noncontractual obligations is the law applicable",
	"situation where they are mandatory irrespective of the law otherwise applicable to the noncontractual obligation",
	"the law governing the noncontractual obligation in question is any law",
	"If a creditor has a claim against several debtors who are liable for the same claim, and one of the debtors has already satisfied the claim in whole or in part, the question of that debtor’s right to demand compensation from the other debtors shall be governed by the law applicable to that debtor’s noncontractual obligation towards the creditor.",
	"The law governing a noncontractual obligation under this Regulation shall apply to the extent that, in matters of noncontractual obligations, it contains rules which raise presumptions of law or determine the burden of proof.",
	"the law applicable to such noncontractual obligations is the law applicable",
	"the law governing the noncontractual obligation in question is that law",
	"Whereas no substantial change is intended as compared with Article 3(3) of the 1980 Convention on the Law Applicable to Contractual Obligations (1) (the Rome Convention), the wording of this Regulation is aligned as far as possible with Article 14 of Regulation (EC)"
]

sentence_summariser = NeuralSentenceSummariser(SUMMARISER_DEFAULT_OPTIONS)
print(sentence_summariser.summarise_sentence(' '.join(map(sentence_summariser.sentify, answer_list))))

# summary_tree = sentence_summariser.summarise_sentence_list(answer_list, tree_arity=5, depth=1)
# print(json.dumps(summary_tree, indent=4))

# s_list = [sentence_summariser.summarise_sentence(a)[0] for a in answer_list]
# print(json.dumps(s_list, indent=4))
# print(sentence_summariser.summarise_sentence(' '.join(map(sentence_summariser.sentify, s_list))))

