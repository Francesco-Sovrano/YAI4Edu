Vue.component("bvaExplorer", {
	template: `
		<overview_area :overview_api="overview_api">
			<h1>BVA-Explorer</h1>
			<br>
			
			<p>
				Here you can ask questions concerning the <a href="https://search.usa.gov/search?affiliate=bvadecisions&sort_by=&query=ptsd" target="_blank">Board of Veterans' Appeals</a>.
				<br>
				<b>N.B.</b> This app has limited capacity, it can only search amongst a few thousands BVA decisions about PTSD.
			</p>
			<answer 
				:input_placeholder="question_input_placeholder" 
				:default_value="question_input_default_value"
				:answer_api="answer_api"
			></answer>
		</overview_area>
	`,
	data() {
		return {
			question_input_placeholder: 'Write a question (i.e., Does combat participation prove service connection?)',
			question_input_default_value: 'Does combat participation prove service connection?',

			answer_api: GET_ANSWER_BVA_API,
			overview_api: GET_OVERVIEW_BVA_API,
		}
	},
});