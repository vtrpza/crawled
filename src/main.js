import './style.css'
import { mount } from 'svelte'
import App from './AppEnhanced.svelte'

// Mount the Svelte application
const app = mount(App, {
  target: document.getElementById('root')
})