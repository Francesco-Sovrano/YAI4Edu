var app = new Vue({
	el: '#app',
	data: {
		stage: 1,
		time_limit: 90*60,
		warning_threshold: 30*60,
		alert_threshold: 10*60,
		topic: 'legal memorandum appropriate for the U.S. legal system',
		book: 'myf:excerpts.akn',
		results_dict: {},
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