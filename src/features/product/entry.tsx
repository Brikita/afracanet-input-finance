import React from 'react'
import { createRoot } from 'react-dom/client'
import { ProductPage } from './ProductPage'
import '../../styles/fonts.css'
import '../../styles.css'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ProductPage />
  </React.StrictMode>,
)
