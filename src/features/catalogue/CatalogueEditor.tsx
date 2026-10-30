import { useState } from 'react'
import { Plus, X } from 'lucide-react'
import type { Product } from '../../domain/models'
import type { Requester } from '../../lib/api'
type Props = { request: Requester; onSaved: () => Promise<void> }
export function CatalogueEditor({
  products,
  request,
  onSaved,
}: Props & { products: Product[] }) {
  const [editing, setEditing] = useState<Product | null>(null)
  const [form, setForm] = useState({
    id: '',
    name: '',
    category: 'Fertilizer',
    unit: '',
    price: '',
    stock: '0',
  })
  const [open, setOpen] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  function edit(product?: Product) {
    setEditing(product ?? null)
    setError('')
    setNotice('')
    setOpen(true)
    setForm(
      product
        ? {
            ...product,
            price: (product.price_cents / 100).toFixed(2),
            stock: String(product.stock),
          }
        : {
            id: '',
            name: '',
            category: 'Fertilizer',
            unit: '',
            price: '',
            stock: '0',
          },
    )
  }
  async function save(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    setNotice('')
    try {
      if (!/^\d+(\.\d{1,2})?$/.test(form.price))
        throw new Error(
          'Enter a positive USD price with at most two decimal places.',
        )
      const [dollars, fraction = ''] = form.price.split('.')
      const price_cents =
        Number(dollars) * 100 + Number(fraction.padEnd(2, '0'))
      const result = await request<{ message: string }>(
        '/products/' + encodeURIComponent(form.id),
        {
          name: form.name,
          category: form.category,
          unit: form.unit,
          price_cents,
          stock: Number(form.stock),
          revision: editing?.revision ?? null,
        },
        'PUT',
      )
      setOpen(false)
      setNotice(result.message)
      await onSaved()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="management-panel">
      <div className="management-heading">
        <div>
          <h3>Maintain your catalogue</h3>
          <p className="muted">
            Update stock counts and future prices. Existing orders keep the
            quantities and prices confirmed by the farmer.
          </p>
        </div>
        <button
          className="button secondary"
          onClick={() => edit()}
          disabled={busy}
        >
          <Plus size={16} /> Add product
        </button>
      </div>
      {notice && (
        <div role="status" className="alert notice">
          {notice}
        </div>
      )}
      <div className="management-buttons">
        {products.map((product) => (
          <button
            key={product.id}
            className="button secondary"
            disabled={busy}
            onClick={() => edit(product)}
          >
            Edit {product.name} {product.unit}
          </button>
        ))}
      </div>
      {open && (
        <form className="catalogue-form" onSubmit={(e) => void save(e)}>
          <div className="management-heading">
            <h3>{editing ? 'Edit product' : 'New product'}</h3>
            <button
              type="button"
              aria-label="Close product editor"
              disabled={busy}
              onClick={() => setOpen(false)}
            >
              <X size={18} />
            </button>
          </div>
          <div className="management-fields">
            {(
              [
                { key: 'id', label: 'Product ID' },
                { key: 'name', label: 'Product name' },
                { key: 'category', label: 'Category' },
                { key: 'unit', label: 'Unit / pack size' },
                { key: 'price', label: 'Unit price (USD)' },
                { key: 'stock', label: 'On-hand stock' },
              ] as const
            ).map((field) => (
              <label key={field.key} className="input-label">
                {field.label}
                <input
                  required
                  value={form[field.key]}
                  disabled={busy || (field.key === 'id' && editing !== null)}
                  maxLength={
                    field.key === 'name'
                      ? 120
                      : field.key === 'category'
                        ? 60
                        : 80
                  }
                  type={field.key === 'stock' ? 'number' : 'text'}
                  min={
                    field.key === 'stock' ? (editing?.reserved ?? 0) : undefined
                  }
                  step={field.key === 'stock' ? 1 : undefined}
                  inputMode={field.key === 'price' ? 'decimal' : undefined}
                  onChange={(e) =>
                    setForm({ ...form, [field.key]: e.target.value })
                  }
                />
              </label>
            ))}
          </div>
          <p className="fine-print">
            {editing
              ? `${editing.reserved} units reserved when this edit opened. `
              : ''}
            Stock is the total on hand, including reservations. Concurrent
            changes require reopening the editor.
          </p>
          {error && (
            <div role="alert" className="alert error">
              {error}
            </div>
          )}
          <button className="button primary" type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save product'}
          </button>
        </form>
      )}
    </div>
  )
}
