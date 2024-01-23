const FULL_DASH_ARRAY = 283;

Vue.component("baseTimer", {
  template: `
  <div class="base-timer">
    <svg class="base-timer__svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <g class="base-timer__circle">
        <circle class="base-timer__path-elapsed" cx="50" cy="50" r="45"></circle>
        <path
          :stroke-dasharray="circleDasharray"
          class="base-timer__path-remaining"
          :class="remainingPathColor"
          d="
            M 50, 50
            m -45, 0
            a 45,45 0 1,0 90,0
            a 45,45 0 1,0 -90,0
          "
        ></path>
      </g>
    </svg>
    <span class="base-timer__label">{{ formattedTimeLeft }}</span>
  </div>
  `,
  props: {
    time_limit: {
      type: Number,
      default: 20,
    },
    warning_threshold: {
      type: Number,
      default: 10,
    },
    alert_threshold: {
      type: Number,
      default: 5,
    },
    finish_fn: {
      type: Function,
      default: function () {}
    },
  },
  data() {
    return {
      timePassed: 0,
      timerInterval: null,
    };
  },
  computed: {
    circleDasharray() {
      return `${(this.timeFraction * FULL_DASH_ARRAY).toFixed(0)} ${FULL_DASH_ARRAY}`;
    },

    formattedTimeLeft() {
      const timeLeft = this.timeLeft;
      const minutes = Math.floor(timeLeft / 60);
      let seconds = timeLeft % 60;

      if (seconds < 10) {
        seconds = `0${seconds}`;
      }

      return `${minutes}:${seconds}`;
    },

    timeLeft() {
      return this.time_limit - this.timePassed;
    },

    timeFraction() {
      const rawTimeFraction = this.timeLeft / this.time_limit;
      return rawTimeFraction - (1 / this.time_limit) * (1 - rawTimeFraction);
    },

    remainingPathColor() {

      if (this.timeLeft <= this.alert_threshold) {
        return "red";
      } else if (this.timeLeft <= this.warning_threshold) {
        return "orange";
      } else {
        return "green";
      }
    }
  },

  watch: {
    timeLeft(newValue) {
      if (newValue === 0) {
        this.onTimesUp();
      }
    }
  },

  mounted() {
    this.startTimer();
  },

  methods: {
    onTimesUp() {
      clearInterval(this.timerInterval);
      this.finish_fn({'Time Passed': this.timePassed});
    },

    startTimer() {
      this.timerInterval = setInterval(() => (this.timePassed += 1), 1000);
    }
  }
});
