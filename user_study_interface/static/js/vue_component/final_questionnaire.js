
Vue.component("finalQuestionnaire", {
  template: `
  <b-container fluid>
    <h1><u>Final Questionnaire</u></h1>
    <br>
    <b-row class="my-1">
      <b-col sm="2">
        <label for="textarea-auto-height">What do you think about the explanations and how would you improve them?</label>
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
      qualitative_feedback: '',
    }
  },
  methods: {
    submit: function() {
      this.finish_fn({
        'qualitative_feedback': this.qualitative_feedback,
      });
    },
  },
  
});
