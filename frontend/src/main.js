import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import * as icons from '@element-plus/icons-vue'

const app = createApp(App)

Object.keys(icons).forEach(key => {
    app.component(key, icons[key])
})

app.use(ElementPlus)
app.mount('#app')