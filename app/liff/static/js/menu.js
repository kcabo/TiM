
Vue.component('form-component', {
  data: function () {
    return {
      showChoices: false
    }
  },
  // props: {
  //   name: String,
  //   content: String,
  //   choices: Array
  // },
  props: ['name', 'content', 'choices'],
  template: `
  <div class="form-unit">
    <div class="filler"> </div>
    <label class="form-name" for="ta1">{{name}}</label>
    <div class="toggle-button" v-bind:class="{active: showChoices}"
    v-on:touchend.prevent="showChoices=!showChoices"
    v-on:click.prevent="showChoices=!showChoices">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 20">
        <defs/>
        <path fill="#AFBFC9" d="M16 2h-4.18C11.4.84 10.3 0 9 0 7.7 0 6.6.84 6.18 2H2C.9 2 0 2.9 0 4v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H4v-2h7v2zm3-4H4v-2h10v2zm0-4H4V6h10v2z"/>
      </svg>
    </div>
    <div class="form-wrapper">
      <textarea id="ta1" rows="1" v-model="content" ref="area"></textarea>
      <div class="delete-icon" v-show="showDelete"
      v-on:touchend.prevent="content=''"
      v-on:click.prevent="content=''">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
          <defs/>
          <path fill="#AFBFC9" d="M7 0C3.13337 0 0 3.13425 0 7c0 3.8658 3.13337 7 7 7 3.8666 0 7-3.1342 7-7 0-3.86575-3.1334-7-7-7zm3.2436 9.00638c.1641.16406.2563.38659.2563.61862 0 .23203-.0922.4546-.2563.6186-.164.1641-.38657.2563-.6186.2563-.23203 0-.45456-.0922-.61862-.2563L7 8.23725 4.99362 10.2436c-.08107.0816-.17746.1463-.28362.1904-.10617.0442-.22002.0669-.335.0669-.11498 0-.22883-.0227-.335-.0669-.10616-.0441-.20255-.1088-.28362-.1904-.08133-.0812-.14585-.1776-.18987-.28374-.04403-.10615-.06669-.21994-.06669-.33486s.02266-.22871.06669-.33486c.04402-.10615.10854-.20258.18987-.28376L5.76275 7 3.75638 4.99362c-.16407-.16406-.25625-.38659-.25625-.61862 0-.23203.09218-.45456.25625-.61862.16406-.16407.38659-.25625.61862-.25625.23203 0 .45456.09218.61862.25625L7 5.76275l2.00638-2.00637c.16406-.16407.38659-.25625.61862-.25625.23203 0 .4546.09218.6186.25625.1641.16406.2563.38659.2563.61862 0 .23203-.0922.45456-.2563.61862L8.23725 7l2.00635 2.00638z"/>
        </svg>
      </div>
    </div>
    <div class="shorthand-group" v-show="showChoices">
      <div class="insert-btn">50*1*1</div>
      <div class="insert-btn">allout</div>
    </div>
  </div>
  `,
  computed: {
    showDelete: function () {
      return Boolean(this.content)
    }
  },
  watch: {
    content: function () {
      const textarea = this.$refs.area;
      textarea.style.height = 'auto';
      this.$nextTick(() => {
        textarea.style.height = textarea.scrollHeight + 'px'
      });
    }
  }
})

const app = new Vue({
  el: '#app',
  delimiters: ['${', '}'],
  data: {
    category: {
      name: 'カテゴリ',
      content: 'aaa',
      choices: ['Swim', 'Dive']
    },
    description: {
      name: '説明',
      content: '',
      choices: ['Swim', 'Dive']
    },
    cycle: {
      name: 'サイクル',
      content: '',
      choices: ['Swim', 'Dive']
    },
  },
  methods: {
    submit: function () {
      let result = this.category.content;
      alert(result);
    }

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
