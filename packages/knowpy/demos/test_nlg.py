import numpy as np
import json
import sys

from knowpy.models.model_manager import ModelManager

query_txt = "What is a noncontractual obligation?"
content_txt = '. '.join(map(lambda x: x.capitalize(), [
	"obligations: a legal agreement specifying a payment or action and the penalty for failure to comply",
	"noncontractual obligation including payment of amounts is a obligations",
	"contractual obligations in provisions of community law is a obligations",
	"noncontractual obligation under this regulation is a obligations",
	"obligations arising out of violations of privacy",
	"contractual obligation under this regulation is a obligations",
	"their obligations towards the creditor is a obligations",
	"obligations arising from infringement of an intellectual property",
	"obligations arising from infringements of intellectual property rights",
	"obligations arising out of violations of privacy including defamation",
	"noncontractual obligations in civil matters is a obligations",
	"contractual obligation is a obligations",
	"contractual obligations in civil matters is a obligations",
	"relating to obligations with regard to particular matters",
	"obligations arising from infringement of a unitary community intellectual property",
	"noncontractual obligation in respect of the liability of a person in the capacity of a worker is a obligations",
	"noncontractual obligation is a obligations",
	"noncontractual obligation in question is a obligations",
	"obligations arising out of restriction of competition",
	"obligations is relating",
	"obligations arising out of environmental damage",
	"obligations is a written_agreement",
	"in matters of obligations contains rules which raise presumptions of laws or",
	"obligations concerns relationships",
	"noncontractual obligations that are likely to arise is a obligations",
	"obligations under regulations",
]))
# query_embedder = ModelManager({'tf_model': 'USE_QA'})
content_embedder = ModelManager({
	'tf_model': {
		'url': 'https://tfhub.dev/google/universal-sentence-encoder-large/5', # Transformer
		# 'url': 'https://tfhub.dev/google/universal-sentence-encoder/4', # DAN
		'cache_dir': '/Users/toor/Documents/Software/DLModels/tf_cache_dir/',
	},
})
# embedded_query = query_embedder.embed([query_txt], as_question=True)[0]
embedded_content = content_embedder.embed([content_txt], as_question=False)[0]

# imports
import torch
from transformers import GPT2Tokenizer
from trl.gpt2 import GPT2HeadWithValueModel, respond_to_batch
from trl.ppo import PPOTrainer

# get models
gpt2_model = GPT2HeadWithValueModel.from_pretrained('gpt2')
gpt2_model_ref = GPT2HeadWithValueModel.from_pretrained('gpt2')
gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# initialize trainer
ppo_config = {'batch_size': 1, 'forward_batch_size': 1}
ppo_trainer = PPOTrainer(gpt2_model, gpt2_model_ref, **ppo_config)

# encode a query
query_tensor = gpt2_tokenizer.encode(query_txt, return_tensors="pt")

while True:
	# get model response
	response_tensor  = respond_to_batch(gpt2_model, query_tensor, txt_len=20)
	response_txt = gpt2_tokenizer.decode(response_tensor[0,:])

	# define a reward for response
	# (this could be any reward such as human feedback or output from another model)
	# query_embedded_response = query_embedder.embed([(response_txt,'')], as_question=False)[0]
	# response_quality = -np.linalg.norm(query_embedded_response-embedded_query)
	content_embedded_response = content_embedder.embed([response_txt], as_question=False)[0]
	dot = np.dot(content_embedded_response, embedded_content)
	norma = np.linalg.norm(content_embedded_response)
	normb = np.linalg.norm(embedded_content)
	response_quality = dot / (norma * normb)

	print(response_quality, response_txt)

	# train model with ppo
	reward = torch.tensor([response_quality]) 
	train_stats = ppo_trainer.step(query_tensor, response_tensor, reward)
