# https://towardsdatascience.com/simple-abstractive-text-summarization-with-pretrained-t5-text-to-text-transfer-transformer-10f6d602c426
import os
from transformers import *

# The models that this pipeline can use are models that have been fine-tuned on a summarization task, which is currently, ‘bart-large-cnn’, ‘t5-small’, ‘t5-base’, ‘t5-large’, ‘t5-3b’, ‘t5-11b’. See the up-to-date list of available models on huggingface.co/models.
FRAMEWORK = 'pt'
MODEL = 'sshleifer/distilbart-xsum-12-6'
TRANSFORMERS_CACHE = os.path.join('/Users/toor/Desktop/Multi-Sentence Compression/[2019]Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer/models/',MODEL.replace('/','-'))
if not os.path.isdir(TRANSFORMERS_CACHE):
    os.mkdir(TRANSFORMERS_CACHE)

concept = 'an obligation'

common_sentence_list = [
    "the obligation is:: an obligation is a course of action that someone is required to take, whether legal or moral., a legal agreement specifying a payment or action and the penalty for failure to comply, a personal relation in which one is indebted for a service or favor, a written promise to repay a debt, the state of being obligated to do or pay something",
    "an obligation of a company",
    "purpose of the obligation",
    "obligation towards the creditor is an obligation",
    "the obligation in question is an obligation",
    "an obligation of the company or body",
    "the conditions under which the assignment can be invoked against the debtor whether an obligation have been discharged",
    "an obligation under the bill",
    "an obligation arising by reason of death",
    "the manner in which an obligation may be extinguished",
    "an obligation that would have been likely to arise",
    "the obligations under such other negotiable instruments is an obligation",
    "obligation constituting the terms and a condition governing the issuance",
    "an obligation arising out of an act performed without due authority in connection with the affairs of another person",
    "an obligation irrespective of a company",
    "an insurance contract shall not satisfy an obligation"
]

question = "What is {concept}?"
answer = "{concept} is"
sentence_list = common_sentence_list + [
    "obligation is document",
    "an obligation including the obligations",
    "particular obligations is the obligation",
    "obligation shall include the obligations",
    "the obligations of the company is obligation",
    "that law applicable to an obligation",
    "an obligation arising from a family relationship, parentage, marriage",
    "otherwise applicable, relating to: an obligation",
    "an obligation arising out of restrictions",
    "indebtedness is an obligation",
    "obligation exclusively in a question",
    "an obligation on which a claim is based",
    "an obligation arising out of nuclear damage",
    "respect abroad of an obligation",
    "a right as obligations",
    "a total breach of an obligation",
    "those persons or a right or the obligation under the trust",
    "an obligation under: bills of exchange, such other negotiable instruments, the treaties",
    "an obligation arising out of an act of unfair competition",
    "an obligation arising out of that unjust enrichment",
    "an obligation abroad of all the member states",
    "obligations of: an officer, auditors",
    "the rule in which the harmful act was committed, even where an obligation is governed by the law of another country",
    "the obligations or and the obligations",
    "an obligation arising out of violations of privacy relating to personality",
    "matters irrespective of: an obligation, obligations",
    "if a noncontractual obligation arising out of an act performed without due authority in connection with the affairs of another person concerns a relationship existing between the parties, such as one arising out of a contract or a tort/delict, that is closely connected with an obligation, it shall be governed by the law that governs that relationship.",
    "obligation arising out of the use of ships",
    "a total breach, law irrespective of an obligation",
    "protecting the rights of workers and an obligation",
    "a limitation of obligations",
    "the obligations for the obligations of the company or body and the obligations",
    "an obligation arising out of: a restriction of competition, a tort/delict, an act of unfair competition, an act performed without due authority in connection with the affairs of another person, damage caused, environmental damage sustained as a result of such damage, nuclear damage, that unjust enrichment, the obligations, the relations between the settlors, of a trust created voluntarily, violations of privacy relating to personality, including defamation",
    "obligations for: acts in the exercise of state authority, the acts of another person",
    "which constitute a financial instrument and a right and an obligation constituting the terms and conditions governing the issuance or offer to the public and public takeover bids of transferable securities",
    "the law governing the obligations",
    "an obligation arising under bills of exchange to the extent that the obligations under such other negotiable instruments arise out of the obligations under such other negotiable instruments negotiable character",
    "a state or and obligations",
    "obligations of officers and members",
    "an obligation presenting a direct link with the dealings prior to conclusion of the contract",
    "relation between those persons or the court or courts of a member state on which a trust instrument has conferred jurisdiction rights or an obligation under the trust",
    "the existence, the nature and the assessment of damage or a remedy claimed; (d) within the limits of powers conferred on the court by the court procedural law, the measures which a court may take to prevent or terminate injury or damage or to ensure the provision of compensation; (e) the question whether a right to claim damages or a remedy may be transferred, including by inheritance; (f) persons entitled to compensation for damage sustained personally; (g obligations; (h) the manner in which an obligation may be extinguished and rules of prescription and limitation, including rules relating to the commencement, interruption and suspension of a period of prescription or limitation.",
    "obligations irrespective of an officer",
    "a limitation, any division, extent of obligations",
    "obligations from the use or operation of a ship, a court substituted for this purpose by the internal law of that member state",
    "a reference to rights and obligations",
    "the obligations should include payment of amounts wrongly received",
    "exchange obligations"
]

question = "What is the purpose of {concept}?"
answer = "The purpose of {concept} is"
sentence_list = [
    "obligation is agreement",
    "an obligation shall include the obligations",
    "enforceable obligation is the obligation",
    "the law of an obligation",
    "the obligations of the company is the obligation",
    "purpose irrespective of the obligation",
    "particular obligations is an obligation",
    "bond is the obligation",
    "the law applicable to an obligation",
    "an obligation exclusively in provisions of community law with regard to particular matters",
    "the obligation towards a creditor",
    "an obligation exclusively in questions",
    "a matter of an obligation",
    "an obligation, the law applicable to the insurance contract",
    "otherwise applicable, relating to: the obligation",
    "the obligation that is likely to arise",
    "the obligation on which a claim is based",
    "note is obligation",
    "indebtedness is the obligation",
    "the obligations to take out the insurance",
    "an obligation exclusively in respect of the liability of a person in the capacity of a worker representing professional interests for damages caused",
    "obligation already in a question",
    "the obligations of the member states under the treaties is the obligation",
    "the purposes of this chapter, that article shall apply to the obligations.",
    "the aim of protecting the rights and an obligation of workers and employers",
    "an obligation has comparable effects",
    "the obligation arising from an infringement of an intellectual property right"
]

question = "What could cause {concept}?"
answer = "{concept} could be caused by"
sentence_list = [
    "the obligation is: an obligation is a course of action that someone is required to take, whether legal or moral.",
    "such obligations is an obligation",
    "relating to an obligation",
    "an obligation in that question",
    "an obligation arising out of environmental damage or the damage sustained by persons or property as a result of such damage",
    "these matters relating to an obligation",
    "a contractual obligation is an obligation",
    "matter of: an obligation, obligations",
    "an obligation is agreement",
    "a matter related to the obligation",
    "respect of an obligation",
    "an obligation either in civil matters",
    "which another member state imposes an obligation",
    "if a noncontractual obligation arising out of an act performed without due authority in connection with the affairs of another person concerns a relationship existing between the parties, such as one arising out of a contract, that is closely connected with an obligation, it shall be governed by the law that governs that relationship.",
    "which the harmful act was committed, even where an obligation is governed by the law of another country",
    "governing the obligation in a question",
    "an obligation shall have comparable effects to marriage",
    "that law that imposes an obligation",
    "obligations to take out insurance",
    "obligation arising out of family relationships and relationship deemed by the law applicable to such relationships",
    "an obligation on which a claim was based",
    "no security, obligation, however described, shall be required of a party who in one member state applies for the enforcement of a judgment given in another member state on the ground that he is a foreign national",
    "those persons or a right or an obligation under the trust",
    "an obligation arising out of restriction of competition",
    "otherwise applicable, relating pursuant to an obligation",
    "a total breach irrespective of an obligation",
    "a matter each relating to obligation",
    "such a case of the obligations",
    "these matters irrespective of: an obligation, obligations"
]

question = "What may justify {concept}?"
answer = "{concept} may be justified by"
sentence_list = [
    "obligation is: a legal agreement specifying a payment or action and the penalty for failure to comply",
    "an obligation shall have comparable effects",
    "rights capable or, an obligation",
    "an obligation either in questions",
    "an obligation to take out insurance unless the insurance contract complies with the specific provisions relating to that insurance laid down",
    "a risk for which a member state imposes an obligation",
    "obligation arising out of another contract",
    "law that imposes an obligation",
    "an obligation, comparable effects may include the obligations",
    "note is an obligation",
    "an obligation arising out of environmental damage or damage sustained by persons or property as a result of such damage"
]

sentence_iter = sentence_list
sentence_iter = map(lambda x: x.strip(), sentence_iter)
# answer = answer.replace('{concept}',concept).strip()
# sentence_iter = map(lambda x: ' '.join((answer, x)), sentence_iter)
question = question.replace('{concept}',concept).strip()
sentence_iter = map(lambda x: ' '.join((question, x.capitalize())), sentence_iter)
sentence_iter = map(lambda x: x.capitalize(), sentence_iter)
text = ' '.join([
    # question.replace('{concept}',concept).capitalize().strip(),
    # answer.replace('{concept}',concept).capitalize().strip(),
    '. '.join(sentence_iter)
])+'.'

preprocess_text = text.strip().replace("\n","")
print ("original text preprocessed: \n", preprocess_text)

config = AutoConfig.from_pretrained(MODEL, cache_dir=TRANSFORMERS_CACHE) # Download configuration from S3 and cache.
print(config)
model = AutoModelWithLMHead.from_pretrained(MODEL, cache_dir=TRANSFORMERS_CACHE)
tokenizer = AutoTokenizer.from_pretrained(MODEL, cache_dir=TRANSFORMERS_CACHE)

min_length = 5
print('Ratio:', min_length/preprocess_text.count(' '))
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, framework=FRAMEWORK)
summary_ids = summarizer(
    preprocess_text, 
    early_stopping = True, # default False
    length_penalty= 2., # default 1.
    max_length = 200,
    min_length = min_length,
    no_repeat_ngram_size = 3, # default 0
    num_beams = 8, # default 1

    # num_return_sequences = 3, # default 1
    repetition_penalty = 1.15, # default 1 # the higher, the longer the sentence (1.45 is fair)
    # top_k = 50, # default 50
    # do_sample=True, # default False
    # top_p=0.95, # default 1
    # temperature=1., # default 1
)

print("\n\nSummarized text: \n" + 100 * '-')
for i, sample_output in enumerate(summary_ids):
    print(sample_output)
    print(100 * '-')
