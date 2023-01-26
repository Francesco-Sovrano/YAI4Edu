
Vue.component("finalMessage", {
  template: `
  <div>
    <b-card title="Final Message">
        <b-card-text>
          Thank you for your help!
          <span v-if="redirect_link">You can now claim your reward at <a :href="redirect_link">{{redirect_link}}</a>.</span>
          You can now close this page.
        </b-card-text>
      </b-card>
  </div>
  `,
  props: {
    redirect_link: {
      type: String,
      default: null,
    }
  }
});
