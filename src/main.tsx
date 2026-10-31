import React from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './app/App'
import { ProductPage } from './features/product/ProductPage'
import './styles/fonts.css'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {window.location.pathname.replace(/\/$/, '') === '/about' ? (
      <ProductPage />
    ) : (
      <App />
    )}
  </React.StrictMode>,
)
