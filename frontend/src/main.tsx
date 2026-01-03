import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { ThemeProvider } from './components/theme-provider.tsx'
import Clarity from '@microsoft/clarity';

const clarityProjectId = import.meta.env.VITE_CLARITY_PROJECT_ID;
if (clarityProjectId) {
  Clarity.init(clarityProjectId);
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ThemeProvider>
    <App />
  </ThemeProvider>,
)
