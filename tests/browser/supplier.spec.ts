import { test, expect } from '@playwright/test'

test('supplier selection keeps identical products distinct and clears the previous basket', async ({
  page,
}) => {
  await page.route('**/api/state', async (route) => {
    const response = await route.fetch()
    const state = await response.json()
    state.products.push({
      id: 'dealer-two-seed',
      supplier_id: 'dealer-two',
      supplier_name: 'Alternative synthetic dealer',
      name: 'Maize seed',
      unit: '2 kg pack',
      category: 'Seed',
      price_cents: 1800,
      stock: 12,
      reserved: 0,
      revision: 'test-catalogue',
    })
    await route.fulfill({ response, json: state })
  })
  const requestedSuppliers: string[] = []
  await page.route('**/api/assistant', async (route) => {
    requestedSuppliers.push(route.request().postDataJSON().supplier_id)
    await route.fulfill({
      json: {
        items: [{ product_id: 'dealer-two-seed', quantity: 1 }],
        clarification: null,
        mode: 'demo',
      },
    })
  })
  await page.goto('/')
  await page.getByRole('button', { name: 'Farmer experience' }).click()
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await page
    .getByRole('button', { name: 'Add Maize seed 2 kg pack', exact: true })
    .click()
  await expect(
    page.getByLabel('Quantity for Maize seed 2 kg pack'),
  ).toHaveValue('1')
  await page.getByLabel('Choose your supplier').selectOption('dealer-two')
  await expect(
    page.getByText('Your basket is ready for inputs.', { exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole('button', { name: 'Confirm input request' }),
  ).toBeDisabled()
  await expect(
    page.getByRole('button', { name: 'Add Maize seed 2 kg pack', exact: true }),
  ).toHaveCount(1)
  await page
    .getByLabel('Describe your input request')
    .fill('I need one 2 kg pack of maize seed.')
  await page.getByRole('button', { name: 'Interpret request' }).click()
  await expect(
    page.getByLabel('Quantity for Maize seed 2 kg pack'),
  ).toHaveValue('1')
  await expect(
    page.getByText('Supplier: Alternative synthetic dealer', { exact: true }),
  ).toBeVisible()
  expect(requestedSuppliers).toEqual(['dealer-two'])
  await page.getByLabel('Choose your supplier').selectOption('supplier-demo')
  await expect(
    page.getByRole('button', { name: 'Confirm input request' }),
  ).toBeDisabled()
})
