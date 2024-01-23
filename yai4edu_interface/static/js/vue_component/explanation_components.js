// ANNOTATED_HTML_CACHE = {};
KNOWN_KNOWLEDGE_GRAPH = [];

Vue.component("template_tree", {
	template: `
		<div>
			<div>
				<span v-html="annotatedText"></span>
				<span v-if="isParent" class="detail_btn" @click="toggle">[{{ isOpen ? 'Less..' : 'More..' }}]</span>
			</div>
			<ul v-if="isOpen && isParent" class="template_tree">
				<li v-for="(child, index) in item.children">
					<template_tree :key="index" :item="child" :annotation_list="annotation_list"></template_tree>
				</li>
			</ul>
		</div>
	`,
	props: {
		item: Object,
		annotation_list: Array,
	},
	data: function() {
		return {
			isOpen: this.item.expanded
		};
	},
	computed: {
		isParent: function() {
			return this.item.children && this.item.children.length;
		},
		annotatedText: function() {
			if (!this.item.text)
				return '';
			// console.log(0, this.item.text);
			// console.log(1, this.item.text.replace('<canvas>', '').replace('</canvas>', ''));
			// var txt = this.item.text.replace(/^\d+\./g, '').replace('&lt;canvas&gt;','');
			var txt = HTMLescape(this.item.text);
			// if (txt in ANNOTATED_HTML_CACHE)
			// 	return ANNOTATED_HTML_CACHE[txt];
			// // console.log('Annotating with:', this.annotation_list);
			// return ANNOTATED_HTML_CACHE[txt] = annotate_html(txt, txt, this.annotation_list, linkify);
			return annotate_html(txt, txt, this.annotation_list, linkify);
		},
	},
	methods: {
		toggle: function() {
			this.isOpen = !this.isOpen;
		},
	}
});

Vue.component("overview_area", {
	template: `
		<div v-on:click="click_fn">
			<b-modal size="lg" v-model="show_overview_modal" scrollable hide-header hide-footer>
				<b-card no-body>
					<b-tabs active-nav-item-class="bg-info" pills card>
						<overview 
							v-for="(card,i) in cards" 
							:key="card.uri" 
							:overview_api="overview_api" 
							:uri="card.uri" 
							:label="card.label" 
							:active_fn="() => i==current_card_index"
							:close_fn="() => {cards.splice(i,1); (cards.length>0)?null:show_overview_modal=false;}"
							:onclick_fn="() => current_card_index=i"
							:annotation_fn="click_fn"
							:with_annotations="with_annotations"
						></overview>
					</b-tabs>
				</b-card>
			</b-modal>
			<slot></slot>
		</div>
	`,
	props: {
		overview_api: {
			type: String,
			required: true,
		},
		with_annotations: {
			type: Boolean,
			default: true,
		},
		// annotate_text: {
		// 	type: Boolean,
		// 	default: true,
		// },
	},
	data() {
		return {
			show_overview_modal: false,
			cards: [],
			current_card_index: 0,
		}
	},
	methods: {
		click_fn: function(e) {
			if (e.type != "click") 
				return;
			var topic = e.target.dataset['topic'] || "";
			var label = e.target.dataset['label'] || "";
			if (!topic)
				return;
			topic = uri_to_prefixed_string(topic);
			// var is_first = (e.target.dataset['is_first'] == 'true');
			var label = titlefy(label);
			const existing_card_idx = this.cards.findIndex(x=>x.uri==topic);
			if (existing_card_idx >= 0)
			{
				this.current_card_index = existing_card_idx;
				this.cards[existing_card_idx].label = label;
			}
			else
			{
				this.cards.push({
					'uri':topic,
					'label':label,
				});
				if (!this.show_overview_modal)
					this.current_card_index = this.cards.length-1;
			}
			this.show_overview_modal = true;
		}
	},
});

Vue.component("overview", {
	template: `
		<b-tab :active="active_fn()" @click="onclick_fn()">
			<template v-slot:title>
				<b-row>
					<b-col col>
						<b-spinner class="my-auto" type="border" small v-if="loading"></b-spinner> {{label}}
					</b-col>
					<b-col col>
						<b-button-close @click="close_fn()">
					</b-col>
				</b-row>
			</template>
			<div v-on:click="annotation_fn">
				<h1>{{ label }}</h1>
				<div class="d-block">
					<p v-if="loading">Loading overview, please wait a while..</p>
					<p v-if="empty">No overview available.</p>
					<b-alert variant="danger" dismissible fade :show="show_error_alert" @dismissed="show_error_alert=false">
						{{error_message}}
					</b-alert>
					<b-container fluid v-if="!loading && !empty">
						<b-row v-if="taxonomical_view.length>0">
							<ul>
								<li v-for="view in taxonomical_view">
									<template_tree :item="view" :annotation_list="annotation_list"></template_tree>
								</li>
							</ul>						
						</b-row>
						<b-row class="scrollspy" v-if="Object.entries(question_overview_tree).length > 1">
							<b-col cols="4">
								<b-list-group v-b-scrollspy="'#listgroup-'+overview_id" style="position:relative; overflow-y:auto; height:300px">
									<b-list-group-item 
										v-for="(overview_tree,question,index) in question_overview_tree" 
										:key="overview_id+'-'+index"
										:href="'#list-item-'+overview_id+'-'+index"
									>
										{{question?question:'Extra'}}
									</b-list-group-item>
								</b-list-group>
							</b-col>
							<b-col cols="8">
								<div :id="'listgroup-'+overview_id" style="position:relative; overflow-y:auto; height:300px">
									<div
										v-for="(overview_tree,question,index) in question_overview_tree"  
										:id="'list-item-'+overview_id+'-'+index" 
										:key="overview_id+'-'+index"
									>
										<h5><b>{{question}}</b></h5>
										<ul style="list-style-type: disclosure-closed;">
											<li v-for="overview in overview_tree">
												<template_tree :item="overview" :annotation_list="annotation_list"></template_tree>
											</li>
										</ul>
									</div>
								</div>
							</b-col>
						</b-row>
						<b-row v-if="Object.entries(question_overview_tree).length == 1"
							v-for="(overview_tree,question,index) in question_overview_tree"
						>
							<h5><b>{{question}}</b></h5>
							<ul style="list-style-type: disclosure-closed;">
								<li v-for="overview in overview_tree">
									<template_tree :item="overview" :annotation_list="annotation_list"></template_tree>
								</li>
							</ul>
						</b-row>
			    	</b-container>
				</div>
			</div>
		</b-tab>
	`,
	props: {
		uri: String,
		label: String,
		explanation_type: {
			type: String,
			default: 'optimal',
		},
		with_annotations: {
			type: Boolean,
			default: true,
		},
		// annotate_text: {
		// 	type: Boolean,
		// 	default: true,
		// },
		overview_api: {
			type: String,
			required: true,
		},
		active_fn: {
			type: Function,
			default: function () {}
		},
		close_fn: {
			type: Function,
			default: function () {}
		},
		onload_fn: {
			type: Function,
			default: function (s,e) {}
		},
		onclick_fn: {
			type: Function,
			default: function (s,e) {}
		},
		annotation_fn: {
			type: Function,
			default: function (s,e) {}
		},
		overview_cache: {
			type: Object,
			default: {},
		},
		taxonomical_view_cache: {
			type: Object,
			default: {},
		},
		annotation_cache: {
			type: Object,
			default: {},
		},
		index: {
			type: Number,
			default: 0,
		}
	},
	computed: {
		href_uri: function() {
			return this.uri.replace(':','-');
		},
		overview_id: function() {
			return this.index+'-'+this.href_uri+'-'+this.explanation_type[0];
		},
	},
	data: function() {
		return {
			loading: true,
			empty: false,
			show_error_alert: false,
			error_message: '',

			question_overview_tree: {},
			taxonomical_view: [],
			annotation_list: [],
		};
	},
	// methods: {
	// 	format_label: function(label) {
	// 		return tokenise(label).filter(x=>x!='').join(' ');
	// 	}
	// },
	created: function() {
		const start_time = (new Date().getTime()) / 1000;
		const self = this;
		const user_id = self.$cookies.get('uuid');
		// self.uri = self.uri.toLowerCase();
		const overview_id = self.uri+'-'+self.label;
		if (overview_id in self.overview_cache)
		{
			self.question_overview_tree = self.overview_cache[overview_id]
			self.taxonomical_view = self.taxonomical_view_cache[overview_id];
			self.annotation_list = self.annotation_cache[overview_id];
			self.loading = false;
			if (!self.question_overview_tree)
				self.empty = true;
			self.onload_fn(start_time, start_time);
			return;
		}
		console.log(user_id, 'is shifting towards topic:', self.uri, self.label);
		self.loading = true;
		$.ajax({
			type: "GET",
			url: self.overview_api,
			responseType:'application/json',
			data: {
				'concept_uri': self.uri, 
				// 'concept_label': self.label, 
				'explanation_type': self.explanation_type,
				'with_annotations': self.with_annotations,
				'uuid': user_id,
			},
			success: function (result) {
				console.log('Processing overview', result);
				self.show_error_alert = false;
				self.loading = false;
				self.onload_fn(start_time, (new Date().getTime()) / 1000);
				// Check cache
				if (!result)
				{
					self.empty = true;
					self.overview_cache[overview_id] = null;
					self.annotation_cache[overview_id] = null;
					self.taxonomical_view_cache[overview_id] = null;
					return;
				}
				self.empty = false;
				// Setup KNOWN_ENTITY_DICT
				const taxonomical_view = tuple_list_to_formatted_jsonld(result.taxonomical_view);
				// Update the known entity dict (cache)
				KNOWN_KNOWLEDGE_GRAPH = KNOWN_KNOWLEDGE_GRAPH.concat(taxonomical_view);
				KNOWN_ENTITY_DICT = get_typed_entity_dict_from_jsonld(KNOWN_KNOWLEDGE_GRAPH);
				// Setup and annotate question summary tree
				const annotation_list = result.annotation_list;
				// IMPORTANT: filter out all the annotations referring to the exact concept in overview.
				// annotation_list = annotation_list.filter(x => x.annotation != self.uri);
				// Populate the question_overview_tree
				var question_summary_tree = result.question_summary_tree;
				if (question_summary_tree)
				{
					for (var [question,summary_tree] of Object.entries(question_summary_tree))
					{
						if (Object.entries(summary_tree).length==0)
							continue;
						// question = question.replace('{X}',self.label);
						if (question.includes('{X}'))
							question = question.replace(' is {X}','').replace(' to {X}','').replace(' of {X}','').replace(' {X}','').replace('{X}','').replace('?','');
						summary_tree = summary_tree_to_jsonld(summary_tree);
						summary_tree = format_jsonld(summary_tree);
						summary_tree = jsonld_to_nestedlist(summary_tree);
						self.question_overview_tree[question] = summary_tree;
					}
				}
				// Set taxonomical_view
				const prefixed_string = prefixed_string_to_uri(self.uri);
				self.taxonomical_view = jsonld_to_nestedlist(nest_jsonld(KNOWN_ENTITY_DICT[prefixed_string], KNOWN_ENTITY_DICT, [prefixed_string], 2));
				// self.annotation_list = self.annotate_text?annotation_list:[];
				self.annotation_list = annotation_list;
				// Cache question summary tree
				self.overview_cache[overview_id] = self.question_overview_tree;
				self.annotation_cache[overview_id] = self.annotation_list;
				self.taxonomical_view_cache[overview_id] = self.taxonomical_view;
			},
			error: function(result) {
				const prefixed_string = prefixed_string_to_uri(self.uri);
				self.loading = false;
				self.onload_fn(start_time, (new Date().getTime()) / 1000);
				if (self.uri in self.annotation_cache)
				{
					self.taxonomical_view = self.taxonomical_view_cache[self.uri];
					self.annotation_list = self.annotation_cache[self.uri];
				}
				else 
				{
					self.error_message = result;
					self.show_error_alert = true;
					// expand_link(
					// 	prefixed_string_to_uri(self.uri), 
					// 	x=>{
					// 		console.log(x);
					// 	}, 
					// 	KNOWN_ENTITY_DICT
					// );
				}
			},
		});
	},
});

Vue.component("answer", {
	template: `
		<div>
			<b-row>
				<b-form-input 
					:placeholder="input_placeholder" 
					type="text" 
					class="mr-4" 
					:aria-label="input_placeholder" 
					aria-describedby="inputGroup-sizing-sm" 
					v-on:keydown.enter="ask"
				></b-form-input>
			</b-row>
			<hr v-if="loading_answers || empty_answers || answer_tree">
			<p v-if="loading_answers">Loading answers, please wait a while..</p>
			<div v-if="empty_answers">
				<div>
					<b-button-close @click="hide()">
				</div>
				<p>No answers found.</p>
			</div>
			<b-alert variant="danger" dismissible fade :show="show_error_alert" @dismissed="show_error_alert=false">
				{{error_message}}
			</b-alert>
			<b-alert variant="warning" dismissible fade :show="show_warning_alert" @dismissed="show_warning_alert=false">
				{{warning_message}}
			</b-alert>
			<div v-if="!loading_answers && !empty_answers && answer_tree">
				<div>
					<b-button-close @click="hide()">
				</div>
				<p>
					<template_tree :item="question_text" :annotation_list="answer_annotation_list"></template_tree>
				</p>
				<div>
					<strong>Answers</strong>:
					<ul class="template_tree">
						<li v-for="answer in answer_tree">
							<template_tree :item="answer" :annotation_list="answer_annotation_list"></template_tree>
						</li>
						<li v-for="quality in answer_quality">
							<template_tree :item="quality" :annotation_list="[]"></template_tree>							
						</li>
					</ul>
				</div>
			</div>
		</div>
	`,
	props: {
		input_placeholder: {
			type: String,
			default: 'Write a question about the system..'
		},
		with_annotations: {
			type: Boolean,
			default: true,
		},
		// annotate_text: {
		// 	type: Boolean,
		// 	default: true,
		// },
		default_value: {
			type: String,
			default: ''
		},
		answer_api: {
			type: String,
			required: true,
		}
	},
	data: function() {
		return {
			show_error_alert: false,
			error_message: '',

			show_warning_alert: false,
			warning_message: '',

			empty_answers: false,
			loading_answers: false,
			question_text: '',
			answer_tree: null,
			answer_annotation_list: [],
			answer_quality: null,
		};
	},
	methods: {
		hide: function() {
			this.empty_answers = false;
			this.loading_answers = false;
			this.answer_tree = null;
			this.show_warning_alert = false;
			this.show_error_alert = false;
		},
		ask: function(event) {
			// console.log(event);
			var self = this;
			var user_id = self.$cookies.get('uuid');
			self.loading_answers = true;
			self.empty_answers = false;
			self.show_warning_alert = false;
			self.show_error_alert = false;

			var x = titlefy(event.target.value.replace(/(\r\n|\n|\r)/gm, "").trim());
			console.log(user_id, 'is sending question:',x);
			$.ajax({
				type: "GET",
				url: self.answer_api,
				responseType:'application/json',
				data: {
					'question': encodeURIComponent(x), 
					'with_annotations': self.with_annotations,
					'uuid': user_id,
				},
				success: function (result) {
					// console.log('Processing answer');
					console.log('Getting as answer:',result);
					self.loading_answers = false;
					if (!result)
					{
						self.empty_answers = true;
						return;
					}
					const annotation_list = result.annotation_list;
					var question_summary_tree = result.question_summary_tree;
					const question = Object.keys(question_summary_tree)[0];
					if (Object.keys(question_summary_tree[question]).length === 0)
					{
						self.empty_answers = true;
						return;
					}
					var summary_tree = summary_tree_to_jsonld(question_summary_tree[question]);
					const answer_quality = result.quality[question];

					self.show_error_alert = false;
					self.empty_answers = false;
					self.question_text = jsonld_to_nestedlist(format_jsonld({'my:question': question}))[0];
					self.answer_tree = jsonld_to_nestedlist(format_jsonld(summary_tree));
					// self.answer_annotation_list = self.annotate_text?annotation_list:[];
					self.answer_annotation_list = annotation_list;
					self.answer_quality = jsonld_to_nestedlist(format_jsonld({'my:answer_quality': pydict_to_jsonld(answer_quality)}));
					
					// Show answer quality
					console.log('Answer quality:', answer_quality);
					if (answer_quality.semantic_similarity < 0.5)
					{
						self.warning_message = 'The following answers can be very imprecise. We struggled to extract them from data, maybe because this question cannot be properly answered using the available information.';
						self.show_warning_alert = true;
					}
				},
				error: function(result) {
					self.error_message = result;
					self.show_error_alert = true;
				},
			});
		},
	}
});

function summary_tree_to_jsonld(summary_tree) {
	var jsonld = {};
	for (var [key,value] of Object.entries(summary_tree))
	{
		if (key == 'children')
			continue;
		if (key == 'extra_info')
		{
			if (value)
			{
				var source_id = prefixed_string_to_uri(summary_tree['source_id']);
				var jsonld_value = tuple_list_to_formatted_jsonld(value);
				KNOWN_KNOWLEDGE_GRAPH = KNOWN_KNOWLEDGE_GRAPH.concat(jsonld_value);
				KNOWN_ENTITY_DICT = get_typed_entity_dict_from_jsonld(KNOWN_KNOWLEDGE_GRAPH);
				// var entity_dict = get_entity_dict_from_jsonld(jsonld_value);
				jsonld['my:hasSource'] = nest_jsonld(KNOWN_ENTITY_DICT[source_id], KNOWN_ENTITY_DICT, [source_id], 2);
			}
		}
		else
			jsonld['my:'+key] = value;
	}
	if (summary_tree.children && summary_tree.children.length)
		jsonld['my:sub_summary_list'] = summary_tree.children.map(summary_tree_to_jsonld);
	return jsonld;
}

function pydict_to_jsonld(pydict) {
	if (isDict(pydict))
	{
		var jsonld = {};
		for (var [key,value] of Object.entries(pydict))
			jsonld['my:'+key] = pydict_to_jsonld(value);
		return jsonld;
	}
	if (isArray(pydict))
		return pydict.map(pydict_to_jsonld);
	return pydict;
}
