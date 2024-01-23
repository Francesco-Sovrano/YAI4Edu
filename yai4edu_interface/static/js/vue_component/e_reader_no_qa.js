Vue.component("eReaderNoQa", {
	template: `
		<div class="mx-3">
			<b-navbar toggleable="lg" variant="dark" type="dark">
				<div id="goal" class="text-white text-wrap text-break">

					<h5>Legal Research and Memo Writing Assignment</h5>
					<br>

					<p>
						This exercise is intended to introduce students to the task of writing a legal memo in an American legal context.
						<br>
						Read the scenario below in less than <b>{{time_limit/60}} minutes</b> and answer the questions following it. For each question, you are asked to make the best short answer you can.
					</p>

					<p v-show="!reading_more">
						<b>Scenario</b>: While working as a mechanic [...] <a href="#" class="text-warning text-decoration-underline" v-on:click="reading_more=true">Read More..</a>
					</p>

					<div v-show="reading_more">

						<p>
							<b>Scenario</b>: While working as a mechanic in the Air Force, Corporal George W. witnessed a fatal air crash on the airfield at Fort Dix, New Jersey. 
							Three people died in the crash of a helicopter that GW was scheduled to work on. 
							GW personally participated in the rescue effort and witnessed the mangled remains of the occupants. 
							This happened four years ago, a year before GW left the air force with a general discharge (not an honorable discharge) due to a period of alcohol abuse on duty. 
							Within the last year, GW has been experiencing morbid flashbacks in which he feels like he is reliving the crash. 
							GW feels generally on edge and has trouble sleeping. 
							He has become dependent on opioids, has dropped out of his night course and has curtailed his social life. 
							A psychological examination by a private therapist diagnosed the veteran with severe anxiety disorders, possibly caused by traumatic experiences, but noted that the symptoms may be aggravated by drug consumption. 
							GW filed a disability claim, but the Veterans Administration (VA) rejected his claim for PTSD as not substantiated. 
						</p>

						<p>
							Let’s assume that you are the American attorney GW has consulted, and that you are planning to prepare a brief legal memo for an appeal to a court called the Board of Veterans Appeals (BVA).
							Please answer the following questions:
							<ol>
								<li> What form will your legal memo take? What sections will it include?
								<li> What are two legal issues that you will address in your memo?
								<li> What kinds of arguments will you make to resolve these legal issues?
							</ol>
						</p>
						
						<p>
							Useful information about preparing a legal memorandum appropriate for the U.S. legal system may be found in the linked excerpts from <b>Brostoff, T. & Sinsheimer, A. (2013). United States Legal Language and Culture: An Introduction to the US Common Law System. Third Edition, Oxford University Press</b>.
						</p>
						
						<p>
							Useful information about BVA cases may be found by searching the BVA case database (linked below) with key words.
						</p>
					</div>

					<p v-show="reading_more" class="text-center">
						<a href="#" class="text-warning text-decoration-underline" v-on:click="reading_more=false">Read Less</a>
					</p>

				</div>

				<div class="ml-auto m-1 text-white">
					<base-timer 
						ref="timer"
						id="timer"
						:time_limit="time_limit" 
						:warning_threshold="warning_threshold" 
						:alert_threshold="alert_threshold"
						:finish_fn="finish_fn"
					></base-timer>
					<b-tooltip target="timer" triggers="hover">
						Time Left
					</b-tooltip>
				</div>
			</b-navbar>
			<br>

			<b-nav tabs>
				<b-nav-item v-on:click="reading=true" :active="reading">e-Reader</b-nav-item>
				<b-nav-item v-on:click="reading=false" :active="!reading">BVA-Explorer</b-nav-item>
			</b-nav>
		
			<hr flex/>

			<overview_area :overview_api="overview_api" v-show="reading">
				<h1>e-Reader</h1>

				<br>
				<p>
					Here you can read some excerpts of the book <b>Brostoff, T. & Sinsheimer, A. (2013). United States Legal Language and Culture: An Introduction to the US Common Law System. Third Edition, Oxford University Press</b>.
					<!--Here you can read some excerpts of <a target="_blank" href="https://books.google.it/books?hl=en&lr=&id=SVsGAQAAQBAJ&oi=fnd&pg=PP2&dq=UNITED+STATES+LEGAL+LANGUAGE+AND+CULTURE+-+AN+INTRODUCTION+TO+THE+US+COMMON+LAW+SYSTEM.pdf&ots=hKm5YdrKYL&sig=wrG2xM0stQfSxF8nzl16TB5_21k#v=onepage&q=UNITED%20STATES%20LEGAL%20LANGUAGE%20AND%20CULTURE%20-%20AN%20INTRODUCTION%20TO%20THE%20US%20COMMON%20LAW%20SYSTEM.pdf&f=false">United States legal language and culture: An introduction to the US common law system</a> and ask any English question about it.-->
				</p>

				<hr flex/>

				<b-alert v-model="showDismissibleAlert" variant="warning" dismissible>
					You can click on <u>underlined words</u> to get an overview of them.
				</b-alert>
				
				<br>		
				<!--<b-form-select v-model="selected_book" required>
					<option :value="null" disabled>Select a tutorial to read</option>
					<option v-for="b in books" :value="b" v-html="b.label"></option>
				</b-form-select>-->
				<vue-pdfjs-wrapper class="mx-auto"
					v-if="selected_book" 
					:pdf-src="selected_book.url" 
				></vue-pdfjs-wrapper>

				<b-row class="my-1 justify-content-md-center">
					<b-col cols="12" md="auto">
						<b-button @click="()=>finish_fn({'Time Passed': $refs.timer.timePassed})" variant="danger" size="lg"><span class="m-auto">Conclude Test</span></b-button>
					</b-col>
				</b-row>

			</overview_area>
			<bva-explorer v-show="!reading"></bva-explorer>

			<br>
			<br>
		</div> 
	`,
	props: {
		book: {
			type: String,
			required: true,
		},
		topic: {
			type: String,
			required: true,
		},
		time_limit: {
			type: Number,
			default: 10*60,
		},
		warning_threshold: {
			type: Number,
			default: 5*60,
		},
		alert_threshold: {
			type: Number,
			default: 1*60,
		},
		finish_fn: {
			type: Function,
			default: function () {}
		},
	},
	data() {
		return {
			question_input_placeholder: 'Write a question (i.e., What is a memorandum?). Note that the questions mentioned in the body of the assignment will not be answered.',
			question_input_default_value: 'Does combat participation prove service connection?',

			books: [
				'myf:excerpts.akn', 
				'myf:introduction_to_basic_legal_citation',
				'myf:law_school_materials_for_success',
				'myf:law_101_fundamentals_of_the_law_new_york_law_and_federal_law',
				'myf:sources_of_american_law_an_introduction_to_legal_research',
			].map( function (x) {
				return {
					'html': template_expand(get_known_label(x), x), 
					'label': get_known_label(x),
					'url': get_RDFItem_description(KNOWN_ENTITY_DICT[prefixed_string_to_uri(x)][prefixed_string_to_uri('my:url')]),
					'name': x
				}
			}),
			selected_book: null,
			reading: true,
			reading_more: false,
			showDismissibleAlert: GET_OVERVIEW_API!=null,

			answer_api: GET_ANSWER_API,
			overview_api: GET_OVERVIEW_API,
		}
	},
	created: function() {
		// this.selected_book = this.books[0].url;
		// this.selected_book = this.books[Math.floor(Math.random() * this.books.length)];
		this.selected_book = this.books.find(e => e['name']==this.book);
	},
});