
var app = new Vue({
  el: '#app',
  delimiters: ['${', '}'],
  data: {
    message: 'これはヘッドメッセージ',
    tweet: 'yeah',
    cycle: '3:00',
    height:"40px"
  },
  computed: {
    styles: function () {
      return {
          "height": this.height,
        }
    }
  },
  watch: {
    tweet: function () {
      this.height = "auto";
      this.$nextTick(()=>{
        this.height = this.$refs.area.scrollHeight + 'px';
      })
    },

    cycle: function () {
      const textarea = this.$refs.area2;
      textarea.style.height = 'auto';
      this.$nextTick(()=>{
        textarea.style.height = textarea.scrollHeight + 'px'
      });
      // const resetHeight = new Promise(function(resolve) {
      //   resolve(textarea.style.height = 'auto')
      // });
      // resetHeight.then(function(){
      //   textarea.style.height = textarea.scrollHeight + 'px'
      // });
    }
  }
});
