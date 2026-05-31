import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import routes from './router/index.js'

// Prism CSS for syntax highlighting
import 'prismjs/themes/prism-tomorrow.css'

// Preload common languages
import 'prismjs/components/prism-python.js'
import 'prismjs/components/prism-javascript.js'
import 'prismjs/components/prism-typescript.js'
import 'prismjs/components/prism-markup.js'
import 'prismjs/components/prism-css.js'
import 'prismjs/components/prism-bash.js'
import 'prismjs/components/prism-json.js'
import 'prismjs/components/prism-yaml.js'
import 'prismjs/components/prism-toml.js'

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
