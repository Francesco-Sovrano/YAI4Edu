import os
# os.environ["CUDA_VISIBLE_DEVICES"]="-1"
from collections import deque

from bottle import run, get, post, route, hook, request, response, static_file
import json
import numpy as np
import random

import time
from more_itertools import unique_everseen
import sys
from server_interface_bva import *

##########################################
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM
correction_tokenizer = AutoTokenizer.from_pretrained("prithivida/grammar_error_correcter_v1")
correction_model     = AutoModelForSeq2SeqLM.from_pretrained("prithivida/grammar_error_correcter_v1")
correction_model     = correction_model.to("cpu")
def correct_grammar(input_sentence, max_candidates=1):
	correction_prefix = "gec: "
	input_sentence = correction_prefix + input_sentence
	input_ids = correction_tokenizer.encode(input_sentence, return_tensors='pt')
	input_ids = input_ids.to("cpu")
	preds = correction_model.generate(
		input_ids,
		do_sample=True, 
		max_length=128, 
		num_beams=7,
		early_stopping=True,
		num_return_sequences=max_candidates
	)
	return [
		correction_tokenizer.decode(pred, skip_special_tokens=True).strip()
		for pred in preds
	][0]
##########################################

_,port,information_units,model_family = sys.argv
port = int(port)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

information_units = information_units.casefold()
model_family = model_family.casefold()
print(f'server {model_family} {information_units}')
qa,qa_cache = init(model_family, information_units)

###############################################################
# CORS

@route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route():
	"""
	This route takes priority over all others. So any request with an OPTIONS
	method will be handled by this function.

	See: https://github.com/bottlepy/bottle/issues/402

	NOTE: This means we won't 404 any invalid path that is an OPTIONS request.
	"""
	add_cors_headers()

@hook('after_request')
def enable_cors_after_request_hook():
	"""
	This executes after every route. We use it to attach CORS headers when
	applicable.
	"""
	add_cors_headers()

def add_cors_headers():
	try:
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
	except Exception as e:
		print('Error:',e)

def get_from_cache(cache, key, build_fn):
	start_time = time.time()
	if key not in cache:
		cache[key] = json.dumps(build_fn())
	print(f'Elapsed seconds: {time.time()-start_time}')
	return cache[key]

###############################################################
# API - Question Answerer

ANSWERS_CACHE = {}
@get('/answer')
def get_answer():
	response.content_type = 'application/json'
	# question = request.forms.get('question') # post
	user_id = request.query.get('uuid')
	question = request.query.get('question')
	if not question.endswith('?'):
		question += '?'
	def build_fn():
		print(f'Answering to {user_id}..')
		# print(question)
		question_answer_dict = get_question_answer_dict(
			qa,
			[question],
			options= OQA_OPTIONS
		)
		print('Summarising..')
		if not question_answer_dict:
			return None
		tree_arity = 1
		question_summary_tree = get_summarised_question_answer_dict(
			qa,
			question_answer_dict,
			options={
				'ignore_non_grounded_answers': False, 
				'use_abstracts': False, 
				'summary_horizon': OQA_OPTIONS['answer_horizon'],
				'tree_arity': tree_arity, 
				# 'cut_factor': 2, 
				'depth': 1,
				'remove_duplicates': False,
				'min_size_for_summarising': float('inf'),
			}
		)
		print('Annotating..')
		result = {
			'question_summary_tree': question_summary_tree,
			'annotation_list': annotate_question_summary_tree(qa, question_summary_tree, is_preprocessed_content=True) if WITH_ANNOTATIONS else [],
			'quality': get_question_answer_dict_quality(qa, question_answer_dict, top=tree_arity),
		}
		if not ANSWERS_CACHE:
			store_cache(qa,qa_cache)
		return result
	return get_from_cache(ANSWERS_CACHE, question, build_fn)

USER_CONTENT_HISTORY_DICT = {}
OVERVIEW_CACHE = {}
@get('/overview')
def get_overview():
	response.content_type = 'application/json'
	user_id = request.query.get('uuid')
	concept_uri = request.query.get('concept_uri')#.lower().strip()
	concept_label = request.query.get('concept_label')
	explanation_type = request.query.get('explanation_type','optimal')
	if ADAPTIVE_QA and MAX_HISTORY_LEN:
		if user_id not in USER_CONTENT_HISTORY_DICT:
			USER_CONTENT_HISTORY_DICT[user_id] = deque(maxlen=MAX_HISTORY_LEN)
		content_history = set(USER_CONTENT_HISTORY_DICT[user_id])
		is_new_content_fn= lambda x: x not in content_history
	else:
		is_new_content_fn= lambda x: True
	print(f'Answering to {user_id}..')

	def build_fn():
		overview_options = dict(OVERVIEW_OPTIONS)
		question_answer_dict = None
		question_summary_tree = None
		################################################################
		################################################################
		### Build query_template_list
		if explanation_type == 'archetypal' or not ADAPTIVE_QA:
			# set consider_incoming_relations to False with concept-centred generic questions (e.g. what is it?), otherwise the answers won't be the sought ones
			query_template_list = [
				'What is {X}?',
				'Why {X}?',
				'How is {X}?',
				'Where is {X}?',
				# 'When is {X}?',
				# # 'Who is {X}?',
				# 'Which {X}?',
				# # 'Whose {X}?',
			]
			overview_options['answer_horizon'] = 2
			overview_options['top_k'] = 100
			overview_options['tfidf_importance'] = 0
			# overview_options['answer_pertinence_threshold'] = 0.5
			# query_template_list = list(map(lambda x: x.replace('{X}',concept_label), query_template_list))
		elif explanation_type == 'optimal':
			# Always put "WHAT" explanations first
			query_template_list = [
				'What is {X}?',
				# 'Why is {X}?',
				# 'How is {X}?',
				# 'Where is {X}?',
				# 'When is {X}?',
				# 'Which {X}?',
				# 'Whose {X}?',
			]
			query_template_list = list(map(lambda x: x.replace('{X}',concept_label), query_template_list))
			# If any, add interesting questions after the "WHAT"
			query_template_list += qa.get_most_interesting_question_list_about_concept(
				concept_uri, 
				adaptivity_options= {
					'is_new_content_fn': is_new_content_fn,
					**ADAPTIVITY_OPTIONS
				},
				**OPTIMAL_ARCHETYPE_IDENTIFICATION_OPTIONS
			)
			query_template_list = list(unique_everseen(map(correct_grammar, query_template_list)))
		else: #if explanation_type == 'random':
			query_template_list = qa.get_question_list_about_concept(
				concept_uri, 
				# **OPTIMAL_ARCHETYPE_IDENTIFICATION_OPTIONS
			)
			random.seed(42)
			random.shuffle(query_template_list)
			query_template_list = query_template_list[:overview_options['question_horizon']]
			query_template_list = list(unique_everseen(map(correct_grammar, query_template_list)))
			overview_options['sort_archetypes_by_relevance'] = False
			overview_options['answer_pertinence_threshold'] = 0.3
		################################################################
		################################################################
		question_answer_dict = get_concept_overview(
			qa, 
			concept_uri= concept_uri,
			concept_label= concept_label, 
			query_template_list= query_template_list,
			options= overview_options,
			is_new_content_fn= is_new_content_fn,
		)
		question_answer_dict = dict(list(question_answer_dict.items())[:overview_options['question_horizon']])
		# # Normalize confidence scores: max is assumed to be 0.1
		# for formatted_answer_list in question_answer_dict.values():
		# 	for answer_dict in formatted_answer_list:
		# 		answer_dict['confidence'] = min(1.,answer_dict['confidence']/0.1)
		# print('Summarising..')
		if question_answer_dict:
			question_summary_tree = get_summarised_question_answer_dict(
				qa, 
				question_answer_dict,
				options={
					'ignore_non_grounded_answers': False, 
					'use_abstracts': False, 
					'summary_horizon': overview_options['answer_horizon'],
					'tree_arity': 1, 
					# 'cut_factor': 1, 
					'depth': 1,
					'remove_duplicates': False,
					'min_size_for_summarising': float('inf'),
				}
			)
		return question_answer_dict, question_summary_tree
	if ADAPTIVE_QA and MAX_HISTORY_LEN:
		question_answer_dict,question_summary_tree = build_fn()
		USER_CONTENT_HISTORY_DICT[user_id] += flatten((map(lambda x: x['sentence'], answer_dict_list) for answer_dict_list in question_answer_dict.values()))
	else:
		question_answer_dict,question_summary_tree = json.loads(get_from_cache(OVERVIEW_CACHE, '-'.join([concept_uri,concept_label if concept_label else concept_uri,explanation_type]), build_fn))
	print('Getting taxonomical view..')
	taxonomical_view = get_taxonomical_view(qa, concept_uri, depth=0)
	if WITH_ANNOTATIONS:
		print('Annotating..')
		annotation_iter = unique_everseen(annotate_question_summary_tree(qa, question_summary_tree, is_preprocessed_content=True) + annotate_taxonomical_view(qa, taxonomical_view, is_preprocessed_content=True))
		equivalent_concept_uri_set = get_equivalent_concepts(qa, concept_uri)
		equivalent_concept_uri_set.add(concept_uri)
		equivalent_concept_label_set = set(flatten(map(lambda x: map(lambda y: y.casefold(), get_label_list(qa,x)), equivalent_concept_uri_set)))
		# annotation_iter = filter(lambda x: x['annotation'] not in equivalent_concept_uri_set, annotation_iter)
		annotation_iter = filter(lambda x: x['text'].casefold() not in equivalent_concept_label_set, annotation_iter)
		annotation_list = list(annotation_iter)
	else:
		annotation_list = []
	return {
		'question_summary_tree': question_summary_tree,
		'taxonomical_view': taxonomical_view,
		'annotation_list': annotation_list,
	}

ANNOTATION_CACHE = {}
@get('/annotation')
def get_annotation():
	response.content_type = 'application/json'
	# question = request.forms.get('question') # post
	sentence = request.query.get('sentence')
	is_preprocessed_content = request.query.get('is_preprocessed_content', True)
	def build_fn():
		print('Annotating..')
		result = annotate_text(qa, sentence, max_concepts_per_alignment=1, is_preprocessed_content=True)
		if not ANNOTATION_CACHE:
			store_cache(qa,qa_cache)
		return result
	return get_from_cache(ANNOTATION_CACHE, sentence, build_fn)

if __name__ == "__main__":
	run(server='meinheld', host='0.0.0.0', port=port, debug=False)
	# run(server='tornado', host='0.0.0.0', port=port, debug=False)
	