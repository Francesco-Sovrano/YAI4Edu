const app = new Vue({
	el: '#app',
	data: {
		stage: 0,
		explanation_options: {
			randomize_explanations: false,
			fast_rating: true,
		},
		timer: {
			time_limit: 0,
			warning_threshold: 3*60,
			alert_threshold: 1*60,
		},
		redirect_link: 'https://app.prolific.co/submissions/complete?cc=C9UYPMRH',
		results_dict: {},
		topic_list: [
			{
				'uri': 'my:memorandum',
				'label': 'memorandum',
				'topic': 'the proper form of a legal memorandum',
				'api': GET_OVERVIEW_API,
			},
			// {
			// 	'uri': 'my:argument',
			// 	'label': 'argument',
			// 	'topic': 'legal argument',
			// 	'api': GET_OVERVIEW_API,
			// },
			// {
			// 	'uri': 'my:proof',
			// 	'label': 'standard of proof',
			// 	'topic': 'the standard of proof',
			// 	'api': GET_OVERVIEW_API,
			// },
			{
				'uri': 'my:disability',
				'label': 'disability',
				'topic': 'the effects of a disability',
				'api': GET_OVERVIEW_API,
			},
			// {
			// 	'uri': 'my:jurisdiction',
			// 	'label': 'jurisdiction',
			// 	'api': GET_OVERVIEW_API,
			// },
			{
				'uri': 'my:element',
				'label': 'elements of the legal standard a veteran needs to satisfy for a PTSD disability claim',
				'topic': 'the elements of the legal standard a veteran needs to satisfy for a PTSD disability claim',
				// 'label': 'elements of the legal standard to satisfy for a disability claim',
				// 'question': 'What are the elements of the legal standard a veteran needs to satisfy for a PTSD disability claim?',
				'api': GET_OVERVIEW_BVA_API,
			},
		],
	},
	methods: {
		finish_step_fn: function(r) {
			this.stage += 1;
			this.results_dict = Object.assign({}, this.results_dict, r);
			// console.log(this.stage, this.results_dict);
		},
		save_results_fn: function(r) {
			this.finish_step_fn(r);
			// this.results_dict['uuid'] = getCookie('uuid');
			const self = this;
			$.ajax({
				url: 'submission', 
				// async: false,
				method:'POST',
				async: false,
				data: {'results_dict': JSON.stringify(this.results_dict)},
				contentType: "application/json; charset=utf-8",
				error: x => {
					alert('Something went wrong! Your answer has not been saved.'); 
					self.stage=0;
				},
			});

		},
	},
});