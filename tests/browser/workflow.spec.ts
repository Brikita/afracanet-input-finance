import { test, expect } from '@playwright/test'

test('farmer, lender, and dealer complete a traceable order', async ({
  page,
}) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/')
  await page.getByRole('button', { name: 'Farmer experience' }).click()
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await expect(
    page.getByRole('heading', { name: 'From your credit to your farm.' }),
  ).toBeVisible()
  await expect(
    page.getByText('Demo request parser · no AI model connected'),
  ).toBeVisible()
  await page
    .getByLabel('Describe your input request')
    .fill('Need 2 bags of DAP')
  await page.getByRole('button', { name: 'Interpret request' }).click()
  await expect(
    page.getByText('Would you like 25 kg or 50 kg bags of DAP?', {
      exact: false,
    }),
  ).toBeVisible()
  await page
    .getByLabel('Describe your input request')
    .fill('Nahitaji mifuko 2 ya DAP ya kilo 50')
  await page.getByRole('button', { name: 'Interpret request' }).click()
  await expect(
    page.getByLabel('Quantity for DAP fertilizer 50 kg bag'),
  ).toHaveValue('2')
  await page.getByRole('button', { name: 'Confirm input request' }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await expect(
    page.getByRole('dialog').getByText('Needs approval', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('lender-demo')
  await page.getByRole('button', { name: 'Open AFC-000001' }).click()
  await page.getByRole('button', { name: 'Approve input order' }).click()
  await expect(
    page.getByRole('dialog').getByText('Ready to invoice', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('supplier-demo')
  await page.getByRole('button', { name: 'Open AFC-000001' }).click()
  await page
    .getByRole('button', { name: 'Confirm stock & issue invoice' })
    .click()
  await expect(
    page.getByRole('dialog').getByText('Awaiting payment', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('lender-demo')
  await page.getByRole('button', { name: 'Open AFC-000001' }).click()
  await page.getByRole('button', { name: 'Simulate lender payment' }).click()
  await expect(
    page.getByRole('dialog').getByText('Ready for collection', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('farmer-amina')
  await page.getByRole('button', { name: 'Open AFC-000001' }).click()
  const code = await page.locator('.pickup-code strong').innerText()
  expect(code).toMatch(/^\d{6}$/)
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('supplier-demo')
  await page.getByRole('button', { name: 'Open AFC-000001' }).click()
  await page.getByLabel("Farmer's collection code").fill('000000')
  await page.getByRole('button', { name: 'Record farmer collection' }).click()
  await expect(page.getByRole('dialog').getByRole('alert')).toContainText(
    'does not match',
  )
  await page.getByLabel("Farmer's collection code").fill(code)
  await page.getByRole('button', { name: 'Record farmer collection' }).click()
  await expect(
    page.getByRole('dialog').getByText('Collected', { exact: true }),
  ).toBeVisible()
  await expect(
    page
      .getByRole('dialog')
      .getByText('Simulated payment confirmed. No money moved.'),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('lender-demo')
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export records' }).click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('afracanet-reconciliation.csv')
  await page.screenshot({
    path: 'data/screenshots/lender-desktop.png',
    fullPage: true,
  })
  expect(errors).toEqual([])
})

test('mobile farmer experience fits without page overflow and prevents overspending', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await page.screenshot({
    path: 'data/screenshots/mobile-login.png',
    fullPage: true,
  })
  await page.getByRole('button', { name: 'Farmer experience' }).click()
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await page.getByLabel('View as').selectOption('farmer-kiptoo')
  await page
    .getByRole('button', { name: 'Add DAP fertilizer 50 kg bag' })
    .click()
  await page.getByLabel('Quantity for DAP fertilizer 50 kg bag').fill('2')
  await expect(
    page.getByText(
      'This order exceeds your available credit. Reduce the quantity.',
    ),
  ).toBeVisible()
  await expect(
    page.getByRole('button', { name: 'Confirm input request' }),
  ).toBeDisabled()
  const fits = await page.evaluate(
    () => document.documentElement.scrollWidth <= window.innerWidth,
  )
  expect(fits).toBe(true)
  await page.screenshot({
    path: 'data/screenshots/farmer-mobile.png',
    fullPage: true,
  })
})
