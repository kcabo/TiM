
const app = new Vue({
  el: '#app',
  delimiters: ['${', '}'],
  data: {
    category: 'Swim',
  },
  methods: {

  },
  computed: {

  },
  watch: {
    category: function () {
      const textarea = this.$refs.category_area;
      textarea.style.height = 'auto';
      this.$nextTick(() => {
        textarea.style.height = textarea.scrollHeight + 'px'
      });
    }
  }
});
