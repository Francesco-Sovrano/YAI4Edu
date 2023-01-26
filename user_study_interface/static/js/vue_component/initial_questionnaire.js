
Vue.component("initialQuestionnaire", {
  template: `
  <div>
    <h1><u>Preliminary Questions and Introduction to the Study</u></h1>

    <b-alert v-model="showDismissibleAlert" variant="warning" dismissible>
      This app is not designed for smartphones or other devices with small screens.
      <br>
      <b>Using a tablet (in landscape mode), laptop or desktop is required</b>.
    </b-alert>

    <br>
    <p>
      Answer the following questions. 
      When finished, you will be able to click the <i>"Start"</i> button.
      <b v-if="time_limit">You will have less than {{time_limit/60}} minutes to complete the study.</b>
    </p>

    <br>
    <b-container fluid>
      <b-row class="my-1" v-for="(qdict,label) in question_dict" :key="label">
        <b-col class="my-auto" sm="3">
          <label>{{ label }}</label>
        </b-col>
        <b-col class="my-auto" sm="9">
          <b-form-input v-if="qdict.type=='number' || qdict.type=='range'" :type="qdict.type" v-model="qdict.value" :state="qdict.value!=null && qdict.value!='' && qdict.value>=qdict.min && qdict.value<=qdict.max" :placeholder="qdict.placeholder" :min="qdict.min" :max="qdict.max"></b-form-input>
          <b-form-input v-if="qdict.type!='select' && qdict.type!='number'" :type="qdict.type" v-model="qdict.value" :state="qdict.value!=null && qdict.value!=''" :placeholder="qdict.placeholder"></b-form-input>
          <b-form-select v-if="qdict.type=='select'" :type="qdict.type" v-model="qdict.value" :state="qdict.value!=null && qdict.value!=''" :options="qdict.options"></b-form-select>
        </b-col>
      </b-row>
      
      <hr flex/>

      <!--<b-row class="my-1">
        <b-col class="my-auto" sm="5">
          <label>Have you written a legal memorandum appropriate for the U.S. legal system? What do you know about legal memoranda?</label>
        </b-col>
        <b-col class="my-auto" sm="7">
          <b-form-textarea :state="background_knowledge.length>0" v-model="background_knowledge"></b-form-textarea>
        </b-col>
      </b-row>

      <hr flex/>-->

      <b-row class="my-1">
        <b-col class="my-auto" sm="5">
          <label>How would you rate your knowledge of <i>the U.S. legal system</i>?</label>
        </b-col>
        <b-col class="my-auto" sm="7">
          <b-form-rating :variant="background_knowledge_rating!=null?'success':'danger'" v-model="background_knowledge_rating"></b-form-rating>
        </b-col>
      </b-row>

      
    </b-container>

    <hr flex/>
    <br>

    <p>
      Click on the <i>"Start"</i> button to begin the study.
      The study consists of evaluating explanations on <b>{{topic_list.length}} different topics</b> in the U.S. legal system.
      <br>
      You will be provided with <b>3 different explanations per topic</b>.
      <b>Rate the explanations on a scale of 0 (bad) to 5 (good) stars.</b>
      <br>
      We will use your anonymous feedback to understand which are the best explanations.
    </p>

    <br>
    <b-button 
      class="float-right mb-2" 
      @click="submit" 
      variant="primary" 
      size="lg"
      :disabled="!can_submit"
    >
      <span class="m-2">Start</span>
    </b-button>
  </div>
  `,
  props: {
    topic_list: Array,
    time_limit: {
      type: Number,
      default: 10*60,
    },
    finish_fn: {
      type: Function,
      default: function (r) {}
    }
  },
  data() {
    return {
      question_dict: {
        // 'What is your school?': {
        //   'type': 'select',
        //   'options': ['Law','Computer Science','Digital Humanities','Physics','Math','Engineering','Others'],
        //   'value': null,
        // },
        'What is your unique Prolific ID?': {
          'type': 'text',
          'value': null,
        },
        'Age': {
          'type': 'number',
          'min': 1,
          'max': 100,
          'value': null,
        },
        'Gender': {
          'type': 'select',
          'options': ['Male','Female', 'Other/Non Binary', 'Prefer not to say'],
          'value': null,
        },
        'Are you a legal expert?': {
          'type': 'select',
          'options': ['Yes','No'],
          'value': null,
        },
        'What is your proficiency in written English?': {
          'type': 'select',
          'options': ['A1 (very low)','A2','B1','B2','C1','C2 (very high)'],
          'value': null,
        },
        'What is your experience in legal writing?': {
          'type': 'select',
          'options': ['None','Low','Medium','High'],
          'value': null,
        },
        
        // 'Average Exam Grade': {
        //   'type': 'select',
        //   'options': ['Low','Average','Better than Average','High','Maximum'],
        //   // 'type': 'number',
        //   // 'placeholder': 'Insert a number in the range [0,100]. If your grade is in [0,4] or [0,30], please convert it to [0,100].',
        //   // 'min': 0,
        //   // 'max': 100,
        //   'value': null,
        // },
      },
      background_knowledge: '',
      background_knowledge_rating: null,
      showDismissibleAlert: true,
    }
  },
  computed: {
    can_submit: function() {
      // if (!this.background_knowledge)
      //   return false;
      if (!this.background_knowledge_rating)
        return false;
      for (var [label,qdict] of Object.entries(this.question_dict))
      {
        if (!qdict.value)
          return false;
      }
      return true;
    },
  },
  methods: {
    submit: function() {
      var result_dict = {
        // 'Background Knowledge': this.background_knowledge, 
        'Background Knowledge Rating': this.background_knowledge_rating,
      }
      for (var [label,qdict] of Object.entries(this.question_dict))
        result_dict[label] = qdict.value;
      this.finish_fn(result_dict);
    },
  },
  
});
