#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import numpy as np
import math
import os

plot_style,file_dir = sys.argv[1],sys.argv[2]

explainer_list = ['optimal','archetypal','random']
topic_to_label_dict = {
	'my:memorandum': 'Memorandum',
	'my:disability': 'Disability',
	'my:element': 'Elements of legal standard',
	'all': 'All 3 topics',
}
explainer_to_label_dict = {
	'optimal': 'intelligent',
	'archetypal': 'archetypal',
	'random': 'random',
}

print('@'*100)
print('Printing statistics')

file_list = [each for each in os.listdir(file_dir) if each.endswith('.json')]
topic_result_dict = {'all':{
	explainer: []
	for explainer in explainer_list+["elapsed_seconds"]
}}
for file in file_list:
	with open(os.path.join(file_dir,file),'r') as f:
		content = json.load(f)
	# if not content.get("Background Knowledge Rating",None) or content["Background Knowledge Rating"] < 4:
	################
	tot_seconds = sum((topic_dict["elapsed_seconds"] for topic_dict in content['evaluation_list']))
	if tot_seconds//60 < 4:
		print('time', tot_seconds, file)
		continue
	################
	smallest_effort = min(topic_dict["elapsed_seconds"] for topic_dict in content['evaluation_list'])
	if smallest_effort < 35:
		print('effort', smallest_effort, file)
		continue
	################
	if content.get("What is your proficiency in written English?",'C1').startswith('A'):
		print('language', file)
		continue
	################
	for topic_dict in content['evaluation_list']:
		topic_label = topic_dict['topic']['uri']
		result_dict = topic_result_dict.get(topic_label,None)
		if not result_dict:
			result_dict = topic_result_dict[topic_label] = {
				explainer: []
				for explainer in explainer_list+["elapsed_seconds"]
			}
		for explainer in explainer_list:
			result_dict[explainer].append(topic_dict["evaluation_dict"][explainer])
			topic_result_dict['all'][explainer].append(topic_dict["evaluation_dict"][explainer])
		result_dict["elapsed_seconds"].append(topic_dict["elapsed_seconds"])
		topic_result_dict['all']["elapsed_seconds"].append(topic_dict["elapsed_seconds"])
for topic, result_dict in topic_result_dict.items():
	print('#'*100)
	print(f'Topic: {topic}')
	for stat, values in result_dict.items():
		value_dict = {
			'mean': f'{np.mean(values)} ± {np.std(values)}',
			'median': f'{np.median(values)} ({np.quantile(values,0.25)},{np.quantile(values,0.75)})',
		}
		print(f'    {stat}: {json.dumps(value_dict, indent=4)}')

aggregated_rate_dict = {explainer: [] for explainer in explainer_list+["elapsed_seconds"]}
for topic, result_dict in topic_result_dict.items():
	for stat, values in result_dict.items():
		aggregated_rate_dict[stat] += values

print('#'*100)
print(f'All topics:')
for stat, values in aggregated_rate_dict.items():
	value_dict = {
		'mean': f'{np.mean(values)} ± {np.std(values)}',
		'median': f'{np.median(values)} ({np.quantile(values,0.25)},{np.quantile(values,0.75)})',
	}
	print(f'    {stat}: {json.dumps(value_dict, indent=4)}')

###############################################################################################################
###############################################################################################################
###############################################################################################################

import scipy.stats as scipy_stats

def common_language_effect_size(x, y, u): # https://en.wikipedia.org/wiki/Mann–Whitney_U_test#Effect_sizes
	return u / (len(x) * len(y))

def rank_biserial_correlation(x, y, u): # https://en.wikipedia.org/wiki/Mann–Whitney_U_test#Effect_sizes
	return 1 - 2 * common_language_effect_size(x, y, u)

#This test can be used to investigate whether two independent samples were selected from populations having the same distribution.
'''
A low pvalue implies that .
A high pvalue implies that Elapsed Seconds in "No" are not statistically greater than Elapsed Seconds in "Yes".
'''
def test_hypothesis(a, b):
	a_value, a_label = a
	b_value, b_label = b
	# params_dict = {}
	# sse_dict = {}
	# for distr, params, sse in best_fit_distribution(a_value):
	# 	sse_dict[distr] = sse
	# 	params_dict[distr] = [params]
	# for distr, params, sse in best_fit_distribution(b_value):
	# 	if distr not in sse_dict:
	# 		continue
	# 	sse_dict[distr] += sse
	# 	params_dict[distr].append(params)
	# best_distribution = sorted(sse_dict.items(), key=lambda x:x[-1])[0][0]
	# fit_params_a, fit_params_b = params_dict[best_distribution]
	alternatives = ['less','greater']
	mannwhitneyu_dict = {}
	for alternative in alternatives:
		u,p = scipy_stats.mannwhitneyu(a_value, b_value, use_continuity=True, alternative=alternative)
		mannwhitneyu_dict[b_label + ' is ' + alternative] = {
			'U': u,
			'p_value': p,
			'common_language_effect_size': common_language_effect_size(a_value, b_value, u),
			'rank_biserial_correlation': rank_biserial_correlation(a_value, b_value, u),
		}
	return {
		# 'wilcoxon': scipy_stats.wilcoxon(a_value,b_value), # The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.
		# 'best_fit_distribution': best_distribution.name,
		# 'params': {
		# 	'a': get_params_description(best_distribution, fit_params_a),
		# 	'b': get_params_description(best_distribution, fit_params_b)
		# },
		'mannwhitneyu': mannwhitneyu_dict,
		# 'kruskal': scipy_stats.kruskal(a_value,b_value), # Due to the assumption that H has a chi square distribution, the number of samples in each group must not be too small. A typical rule is that each sample must have at least 5 measurements.
	}

for topic, result_dict in topic_result_dict.items():
	print('-'*100)
	print(topic)
	print('Random vs Archetypal:', json.dumps(test_hypothesis( # A low mannwhitneyu pvalue (<0.05) implies that Effectiveness in 'No' are statistically lower than Effectiveness in 'Yes'
		(result_dict['random'],'No'),
		(result_dict['archetypal'],'Yes'),
	), indent=4))
	print('Random vs Optimal', json.dumps(test_hypothesis( # A low mannwhitneyu pvalue (<0.05) implies that Effectiveness in 'No' are statistically lower than Effectiveness in 'Yes'
		(result_dict['random'],'No'),
		(result_dict['optimal'],'Yes'),
	), indent=4))
	print('Archetypal vs Optimal', json.dumps(test_hypothesis( # A low mannwhitneyu pvalue (<0.05) implies that Effectiveness in 'No' are statistically lower than Effectiveness in 'Yes'
		(result_dict['archetypal'],'No'),
		(result_dict['optimal'],'Yes'),
	), indent=4))

###############################################################################################################
###############################################################################################################
###############################################################################################################

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def show_values(axs, orient="v", space=.01):
	def _single(ax):
		if orient == "v":
			for p in ax.patches:
				_x = p.get_x() + p.get_width() / 2
				_y = p.get_y() + p.get_height() + (p.get_height()*0.01)
				value = '{:.2f}'.format(p.get_height())
				ax.text(_x, _y, value, ha="center", weight='bold') 
		elif orient == "h":
			for p in ax.patches:
				_x = p.get_x() + p.get_width() + float(space)
				_y = p.get_y() + p.get_height() - (p.get_height()*0.5)
				value = '{:.2f}'.format(p.get_width())
				ax.text(_x, _y, value, ha="left", weight='bold')

	if isinstance(axs, np.ndarray):
		for idx, ax in np.ndenumerate(axs):
			_single(ax)
	else:
		_single(axs)

df_list = []
for i, (topic, result_dict) in enumerate(topic_result_dict.items()):
	result_dict = dict(map(lambda x: (explainer_to_label_dict.get(x[0],x[0]),x[1]), result_dict.items()))
	df_topic = pd.DataFrame(result_dict)
	df_topic = pd.melt(df_topic, value_vars=explainer_to_label_dict.values())
	df_topic['topic'] = topic_to_label_dict.get(topic,topic)
	df_list.append(df_topic)
df = pd.concat(df_list,ignore_index=True)
# print(df)

sns.set(rc={"figure.figsize":(10, 4)}) #width=8, height=4
sns.set_style("whitegrid")
if plot_style == "boxplot":
	ax = sns.boxplot(data=df, x="topic", y="value", hue="variable", showfliers=True, autorange=True)
elif plot_style == "barplot":
	ax = sns.barplot(data=df, x="topic", y="value", hue="variable", errwidth=0)
	show_values(ax)


ax.set_xlabel(ax.get_xlabel().capitalize(), fontsize='x-large', fontweight='bold')
ax.set_ylabel('rate'.capitalize(), fontsize='x-large', fontweight='bold')
plt.ylim(0, 5)

legend = plt.legend(loc='lower left', framealpha=0.95)
frame = legend.get_frame()
frame.set_facecolor('white')

# plt.legend()
plt.tight_layout()
plt.savefig(f'{plot_style}.png')
