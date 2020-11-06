let sendData = function (data, method) {
  return fetch(location.pathname, {
    method: method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then((response) => response.text())
  .catch((error) => alert(error))
}


let formatDate = function (rawDate) {
  // rawDateは文字列型 整数6桁 201009
  let year = '20' + rawDate.substring(0, 2);
  let month = rawDate.substring(2, 4);
  let day = rawDate.substring(4, 6);
  let dateArray = [year, month, day];
  let fullDateStr = dateArray.join('/');
  let time = Date(fullDateStr);
  let date = new Date(time);
  let dayNum = date.getDay();
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
  let weekdayJP = weekdays[dayNum];
  let formatted = dateArray.join('.') + ' ' + weekdayJP;
  return formatted
}


let sendUserMessage = function (message) {
  let data = {
    type: 'text',
    text: message
  };
  liff.sendMessages([data])
  .catch((err) => alert('なぜかメッセージが送れませんでした'));
}


Vue.component('insert-btn', {
  props: {
    char: String
  },
  computed: {
    label: function () {
      if (this.char === '␣') {
        return '<空白>';
      } else if (this.char === '\n') {
        return '<改行>';
      } else {
        return this.char
      }
    }
  },
  template: `
    <div class="insert-btn"
    v-on:touchend.prevent="$emit('insert', char)"
    v-on:click.prevent="$emit('insert', char)">
    {{label}}
    </div>
  `
})


Vue.component('form-unit', {
  data: function () {
    return {
      showChoices: false
    }
  },
  props: {
    name: String,
    value: String,
    choices: Array
  },
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
      <textarea id="ta1" rows="1" v-model="inputValue" ref="area"></textarea>
      <div class="delete-icon" v-show="showDelete"
      v-on:touchend.prevent="inputValue=''"
      v-on:click.prevent="inputValue=''">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
          <defs/>
          <path fill="#AFBFC9" d="M7 0C3.13337 0 0 3.13425 0 7c0 3.8658 3.13337 7 7 7 3.8666 0 7-3.1342 7-7 0-3.86575-3.1334-7-7-7zm3.2436 9.00638c.1641.16406.2563.38659.2563.61862 0 .23203-.0922.4546-.2563.6186-.164.1641-.38657.2563-.6186.2563-.23203 0-.45456-.0922-.61862-.2563L7 8.23725 4.99362 10.2436c-.08107.0816-.17746.1463-.28362.1904-.10617.0442-.22002.0669-.335.0669-.11498 0-.22883-.0227-.335-.0669-.10616-.0441-.20255-.1088-.28362-.1904-.08133-.0812-.14585-.1776-.18987-.28374-.04403-.10615-.06669-.21994-.06669-.33486s.02266-.22871.06669-.33486c.04402-.10615.10854-.20258.18987-.28376L5.76275 7 3.75638 4.99362c-.16407-.16406-.25625-.38659-.25625-.61862 0-.23203.09218-.45456.25625-.61862.16406-.16407.38659-.25625.61862-.25625.23203 0 .45456.09218.61862.25625L7 5.76275l2.00638-2.00637c.16406-.16407.38659-.25625.61862-.25625.23203 0 .4546.09218.6186.25625.1641.16406.2563.38659.2563.61862 0 .23203-.0922.45456-.2563.61862L8.23725 7l2.00635 2.00638z"/>
        </svg>
      </div>
    </div>
    <div class="shorthand-group" v-show="showChoices">
      <insert-btn
        v-for="c in choices"
        v-bind:char="c"
        v-on:insert="insert"
      ></insert-btn>
    </div>
  </div>
  `,
  computed: {
    showDelete: function () {
      return Boolean(this.inputValue)
    },
    inputValue: {
      get: function () {
        return this.value;
      },
      set: function (newValue) {
        this.$emit('input', newValue);
      }
    }
  },
  watch: {
    inputValue: function () {
      const textarea = this.$refs.area;
      textarea.style.height = 'auto';
      this.$nextTick(() => {
        textarea.style.height = textarea.scrollHeight + 'px'
      });
    }
  },
  methods: {
    insert: function (value) {
      this.inputValue += value;
    }
  }
})

const app = new Vue({
  el: '#app',
  delimiters: ['${', '}'],
  data: {
    category: {
      name: 'カテゴリ',
      content: '',
      choices: ['Swim', 'Dive', 'Pull', 'Kick', 'K/P']
    },
    description: {
      name: '説明',
      content: '',
      choices: ['50', '100', '200', '1', '2', '4', '*', 'allout', '␣', '\n']
    },
    cycle: {
      name: 'サイクル',
      content: '',
      choices: ['1:00', '2:00', '3:00', '␣', '\n']
    }
  },
  computed: {
    purpose: function () {
      return location.pathname.split('/').slice(-2)[0];
    },
    date: function () {
      if (this.purpose === 'new-menu') {
        let rawDate = location.pathname.split('/').slice(-1)[0];
        return formatDate(rawDate)
      } else {
        return '2020.01.01 水'
      }
    }
  },
  methods: {
    submit: function () {
      let data = {
        category: this.category.content.replace('␣', ' '),
        description: this.description.content.replace('␣', ' '),
        cycle: this.cycle.content.replace('␣', ' ')
      };
      let purpose = this.purpose
      if (purpose === 'menu' || purpose === 'new-menu') {
        let method = purpose === 'menu' ? 'PUT' : 'POST';
        sendData(data, method).then((responseText) => {
          if (responseText === 'Failed') {
            alert('メニューが見つかりませんでした');
          } else {
            sendUserMessage('$menu=' + responseText);
            liff.closeWindow();
          }
        })
      } else {
        alert('INVALID PATH');
      }
    },
    cancel: function () {
      liff.closeWindow();
    }
  },
  mounted: function () {
    if (this.purpose === 'menu') {
      fetch(location.pathname + '/ajax'
        ).then((response) => response.json()
        ).then((json) => {
          if (json.message === 'Success') {
            let rawDate = String(json.date);
            this.date = formatDate(rawDate);
            this.category.content = json.category;
            this.description.content = json.description;
            this.cycle.content = json.cycle;
          }
        }).catch((error) => alert(error))
    }
  }
});
