
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

      <b-row class="my-1">
        <b-col sm="5">
          <label>Have you written a <i>{{ topic }}</i>? What do you know about legal memoranda?</label>
        </b-col>
        <b-col sm="7">
          <b-form-textarea :state="background_knowledge.length>0" v-model="background_knowledge"></b-form-textarea>
        </b-col>
      </b-row>

      <hr flex/>

      <b-row class="my-1">
        <b-col sm="5">
          <label>How do you rate your knowledge of writing a <i>{{ topic }}</i>?</label>
        </b-col>
        <b-col sm="7">
          <b-form-rating :variant="background_knowledge_rating!=null?'success':'danger'" v-model="background_knowledge_rating"></b-form-rating>
        </b-col>
      </b-row>

      
    </b-container>

    <hr flex/>
    <br>

    <p>
      What follows is the text of the exercise that you are requested to complete.
      After reading it, click on the button <i>"Start Test"</i>.
      Do not worry, you will have the whole text of the assignment at your disposal for the duration of the test.
    </p>

    <div class="border border-dark p-3">

      <b><u>Legal Research and Memo Writing Assignment</u></b>

      <p>
        This exercise is intended to introduce students to the task of writing a legal memo in an American legal context.
      </p>

      <p>
        Read the scenario below in less than <b>{{time_limit/60}} minutes</b> and answer the questions following it. For each question, you are asked to make the best short answer you can.
      </p>

    
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
        Useful information about preparing a legal memorandum appropriate for the U.S. legal system may be found after clicking the "Start Test" button, in the linked excerpts from <b>Brostoff, T. & Sinsheimer, A. (2013). United States Legal Language and Culture: An Introduction to the US Common Law System. Third Edition, Oxford University Press</b>.
      </p>
      
      <p>
        Useful information about BVA cases may be found by searching the BVA case database (available after clicking the "Start Test" button) with key words.
      </p>

    </div>

    <br>
    <b-button 
      class="float-right mb-2" 
      @click="submit" 
      variant="primary" 
      size="lg"
      :disabled="!can_submit"
    >
      <span class="m-2">Start Test</span>
    </b-button>
  </div>
  `,
  props: {
    topic: {
      type: String,
      required: true,
    },
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
        'School': {
          'type': 'select',
          'options': ['Law','Computer Science','Digital Humanities','Physics','Math','Engineering','Others'],
          'value': null,
        },
        'Proficiency in Written English': {
          'type': 'select',
          'options': ['A1','A2','B1','B2','C1','C2'],
          'value': null,
        },
        'Experience in Legal Writing': {
          'type': 'select',
          'options': ['None','Low','Medium','High'],
          'value': null,
        },
        'Age': {
          'type': 'number',
          'min': 1,
          'max': 100,
          'value': null,
        },
        'Average Exam Grade': {
          'type': 'select',
          'options': ['Low','Average','Better than Average','High','Maximum'],
          // 'type': 'number',
          // 'placeholder': 'Insert a number in the range [0,100]. If your grade is in [0,4] or [0,30], please convert it to [0,100].',
          // 'min': 0,
          // 'max': 100,
          'value': null,
        },
        'Gender': {
          'type': 'select',
          'options': ['Male','Female', 'Other/Non Binary', 'Prefer not to say'],
          'value': null,
        },
        
      },
      background_knowledge: '',
      background_knowledge_rating: null,
      showDismissibleAlert: true,
    }
  },
  computed: {
    can_submit: function() {
      if (!this.background_knowledge || !this.background_knowledge_rating)
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
        'Topic':this.topic, 
        'Background Knowledge': this.background_knowledge, 
        'Background Knowledge Rating': this.background_knowledge_rating,
      }
      for (var [label,qdict] of Object.entries(this.question_dict))
        result_dict[label] = qdict.value;
      this.finish_fn(result_dict);
    },
  },
  
});
