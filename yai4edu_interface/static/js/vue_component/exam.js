
Vue.component("exam", {
  template: `
  <b-container fluid>
    <h1><u>Exercise</u></h1>

    <br>
    <p>
      Complete the following assignment without using Google or any other external resources (including books). 
      <br>
      <b>Use only your notes or memory.</b>
    </p>

    <hr flex/><br>

    <b-row class="border border-dark p-3 my-1">

        <div v-html="question"></div>

        <b-form-textarea
          id="textarea-auto-height"
          rows="3"
          v-model="text"
          :state="text.length >= 10"
          placeholder="Enter at least 10 characters"
        ></b-form-textarea>
      
    </b-row>
    
    <br><hr flex/><br>

    <b-row class="my-1">
      <b-col sm="3">
        <label>The system made it easy for me to complete the assignment.</label>
      </b-col>
      <b-col sm="9">
        <b-form-radio-group
          :state="customer_effort_score!=null"
          v-model="customer_effort_score"
          :options="customer_effort_score_options"
          class="mb-3"
        ></b-form-radio-group>
      </b-col>
    </b-row>

    <br><hr flex/><br>

    <b-row class="my-1">
      <b-col sm="2">
        <label for="textarea-auto-height">What do you think about the explanatory tool and how would you improve it?</label>
      </b-col>
      <b-col sm="10">
        <b-form-textarea
          id="textarea-auto-height"
          rows="3"
          v-model="qualitative_feedback"
          placeholder="Please, give us a qualitative feedback"
        ></b-form-textarea>
      </b-col>
    </b-row>

    <br>
    <b-row class="my-1">
      <b-col class="offset-4">
        <b-button 
          class="m-2" 
          @click="submit" 
          variant="success" 
          size="lg"
          :disabled="!can_submit"
        ><span class="m-2">Submit</span></b-button>
      </b-col>
    </b-row>
  </b-container>
  `,
  props: {
    topic: {
      type: String,
      required: true,
    },
    finish_fn: {
      type: Function,
      default: function () {}
    },
  },
  data() {
    return {
      text: '',
      customer_effort_score: null,
      customer_effort_score_options: [
        'Strongly Disagree',
        'Disagree',
        'Somewhat Disagree',
        'Neutral',
        'Somewhat Agree',
        'Agree',
        'Strongly Agree',
      ],
      qualitative_feedback: '',
    }
  },
  computed: {
    can_submit: function() {
      if (!this.customer_effort_score || !this.text)
        return false;
      return true;
    },
    question: function() {
      return `
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
          <li> What are two legal questions you will address in your memo? 
          <li> What form will your legal memo take? What sections will it include?
          <li> What legal issue will you address? What kinds of arguments will you make to resolve the legal issue?
        </ol>
      </p>
      `
    }
  },
  methods: {
    submit: function() {
      this.finish_fn({
        'Question': this.question,
        'Answer': this.text,
        'Customer Effort Score': this.customer_effort_score,
        'Qualitative Feedback': this.qualitative_feedback,
      });
    },
  },
  
});
