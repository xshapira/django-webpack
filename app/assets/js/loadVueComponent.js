import Vue from 'vue';
import Sample from './components/Sample.vue';
import Card from './components/Card.vue';

const app = new Vue({
  el: '#app',
  components: {
    Sample,
    Card
  }
});

export default {
  app
};
