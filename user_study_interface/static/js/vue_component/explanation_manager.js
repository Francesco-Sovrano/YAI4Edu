Vue.component("explanationManager", {
	template: `
		<div>
			<b-navbar v-if="timer.time_limit" toggleable="lg" variant="dark" type="dark">
				<div id="goal" class="text-white text-wrap text-break">

					<b>Task</b>

					<p>
						Evaluate the explanations in a scale from 0 (bad) to 5 (good) stars.
      					We will use your anonymous feedback to understand which are the best explanations.
					</p>
				</div>

				<div class="ml-auto m-1 text-white">
					<base-timer 
						ref="timer"
						id="timer"
						:time_limit="timer.time_limit" 
						:warning_threshold="timer.warning_threshold" 
						:alert_threshold="timer.alert_threshold"
						:finish_fn="finish_fn"
					></base-timer>
					<b-tooltip target="timer" triggers="hover">
						Time Left
					</b-tooltip>
				</div>
			</b-navbar>
			<br v-if="timer.time_limit">
			<div class="mx-5 my-auto p-3 border">
				<p>
					Which one of the following sequences of questions and answers better explains the following topic?
					<br>
					<b>Rate the explanations on a scale of 0 (bad) to 5 (good) stars.</b>
				</p>
			</div>
			<br>
			<div class="m-auto"
				v-for="(topic, index) in topic_list"
				v-show="index==stage"
				:key="index"
			>
				<b-row class="m-auto">
					<h2 class="mx-auto"><b>Topic</b>: {{titlefy(topic.topic)}}</h2>
				</b-row>
				<hr>
				<b-row class="m-auto" style="height:50vh">
					<b-col class="m-auto text-right">
						<b-button v-if="current_explanation > 1" v-on:click="current_explanation--">&laquo; Previous Explanation</b-button>
					</b-col>

					<b-col cols="9">
						<div v-show="current_explanation==1">
							<div class="btn btn-warning btn-block" style="pointer-events: none;"><b>1st Explanation &darr;</b></div>
							<overview 
								:overview_api="topic.api" 
								:uri="topic.uri" 
								:label="topic.label" 
								:index="index"
								:explanation_type="explanation_list[0]"
							></overview>
						</div>
						<div v-show="current_explanation==2">
							<div class="btn btn-warning btn-block" style="pointer-events: none;"><b>2nd Explanation &darr;</b></div>
							<overview
								:overview_api="topic.api" 
								:uri="topic.uri" 
								:label="topic.label" 
								:index="index"
								:explanation_type="explanation_list[1]"
							></overview>
						</div>
						<div v-show="current_explanation==3">
							<div class="btn btn-warning btn-block" style="pointer-events: none;"><b>3rd Explanation &darr;</b></div>
							<overview
								:overview_api="topic.api" 
								:uri="topic.uri" 
								:label="topic.label" 
								:index="index"
								:explanation_type="explanation_list[2]"
							></overview>
						</div>
					
					</b-col>
					<b-col class="m-auto text-left">
						<b-button v-if="current_explanation < 3" v-on:click="current_explanation++">Next Explanation &raquo;</b-button>
					</b-col>
				</b-row>
				<hr>
				<b-row class="m-auto" style="height:10vh" v-show="current_explanation == 1">
					<div class="my-auto col-4 text-right">
						<label>How do you rate the <b>1st</b> explanation?</label>
					</div>
					<div class="my-auto col-5">
						<b-form-rating :variant="eval_exp_1!=null?'success':'danger'" v-model="eval_exp_1" v-on:change="change_explanation"></b-form-rating>
					</div>
				</b-row>
				<b-row class="m-auto" style="height:10vh" v-show="current_explanation == 2">
					<div class="my-auto col-4 text-right">
						<label>How do you rate the <b>2nd</b> explanation?</label>
					</div>
					<div class="my-auto col-5">
						<b-form-rating :variant="eval_exp_2!=null?'success':'danger'" v-model="eval_exp_2" v-on:change="change_explanation"></b-form-rating>
					</div>
				</b-row>
				<b-row class="m-auto" style="height:10vh" v-show="current_explanation == 3">
					<div class="my-auto col-4 text-right">
						<label>How do you rate the <b>3rd</b> explanation?</label>
					</div>
					<div class="my-auto col-5">
						<b-form-rating :variant="eval_exp_3!=null?'success':'danger'" v-model="eval_exp_3" v-on:change="change_explanation"></b-form-rating>
					</div>
				</b-row>
				<b-row class="m-auto">
					<b-button block variant="success" @click="move_to_next_topic" :disabled="!eval_exp_1 || !eval_exp_2 || !eval_exp_3">{{(eval_exp_1 && eval_exp_2 && eval_exp_3)?'Go to next topic':'Rated explanations: '+((eval_exp_1?1:0)+(eval_exp_2?1:0)+(eval_exp_3?1:0))+'/3'}}</b-button>
				</b-row>
			</div>
		</div> 
	`,
	props: {
		topic_list: Array,
		explanation_options: {
			type: Array,
			default: {
				randomize_explanations: false,
				fast_rating: true,
			},
		},
		timer: {
			type: Array,
			default: {
				time_limit: 10*60,
				warning_threshold: 3*60,
				alert_threshold: 1*60,
			},
		},
		finish_fn: {
			type: Function,
			default: function (r) {}
		}
	},
	data() {
		return {
			stage: 0,
			current_explanation: 1,
			overview_api: GET_OVERVIEW_API,
			stage_timestamp: Math.floor(Date.now() / 1000),
			explanation_list: ['archetypal','optimal','random'],
			eval_exp_1: null,
			eval_exp_2: null,
			eval_exp_3: null,
			result_list: []
		}
	},
	methods: {
		shuffle_array: function(array) {
			for (var i = array.length - 1; i > 0; i--) {
				// Generate random number
				const j = Math.floor(Math.random() * (i + 1));
				const temp = array[i];
				array[i] = array[j];
				array[j] = temp;
			}
			return array;
		},
		move_to_next_topic: function() {
			const now = Math.floor(Date.now() / 1000);
			const evaluation_dict = {};
			evaluation_dict[this.explanation_list[0]] = this.eval_exp_1;
			evaluation_dict[this.explanation_list[1]] = this.eval_exp_2;
			evaluation_dict[this.explanation_list[2]] = this.eval_exp_3;
			this.result_list.push({
				'topic': this.topic_list[this.stage],
				'evaluation_dict': evaluation_dict,
				'elapsed_seconds': now - this.stage_timestamp,
			});
			this.stage += 1;
			this.eval_exp_1 = null;
			this.eval_exp_2 = null;
			this.eval_exp_3 = null;
			this.current_explanation = 1;
			this.stage_timestamp = now;
			if (this.stage >= this.topic_list.length)
				this.finish_fn({'evaluation_list': this.result_list});
		},
		change_explanation: function() {
			if (this.explanation_options['fast_rating'])
			{
				if (this.current_explanation==1 && this.eval_exp_2)
					return;
				if (this.current_explanation==2 && this.eval_exp_3)
					return;
				if (this.current_explanation==3 && this.eval_exp_1)
					return;
				if (this.current_explanation==3)
					this.current_explanation = 1;
				else
					this.current_explanation++;
				// // alert('Thank you! Please evaluate also the next explanation.')
			}
		},
	},
	created: function() {
		if (this.explanation_options['randomize_explanations'])
			this.explanation_list = this.shuffle_array(this.explanation_list);
	},
});