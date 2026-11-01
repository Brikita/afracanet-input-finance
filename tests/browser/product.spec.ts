import { test, expect } from '@playwright/test'

test('public product information makes no authenticated, AI or payment API calls', async ({
  page,
}) => {
  const apiRequests: string[] = []
  const errors: string[] = []
  page.on('request', (request) => {
    if (new URL(request.url()).pathname.startsWith('/api/'))
      apiRequests.push(request.url())
  })
  page.on('pageerror', (error) => errors.push(error.message))
  for (const route of ['/about', '/about.html']) {
    await page.goto(route)
    await expect(
      page.getByRole('heading', {
        name: 'A payment you can verify. A case you can follow.',
      }),
    ).toBeVisible()
    await expect(
      page.getByText('No handover recorded', { exact: true }),
    ).toBeVisible()
    await expect(page.locator('.proof-amount strong')).toHaveText('USD 18.00')
  }
  expect(apiRequests).toEqual([])
  expect(errors).toEqual([])
})

test('visitors explore evidence and graph concepts without triggering financial actions', async ({
  page,
}) => {
  const apiRequests: string[] = []
  page.on('request', (request) => {
    if (new URL(request.url()).pathname.startsWith('/api/'))
      apiRequests.push(request.url())
  })
  await page.goto('/about')
  await page.getByRole('button', { name: '7 Collection', exact: true }).click()
  await expect(page.locator('.payment-verdict')).toHaveText('Not recorded')
  await page.getByRole('link', { name: 'Evidence', exact: true }).click()
  await page.getByRole('button', { name: /SACCO & lender records/ }).click()
  await expect(page.locator('#source-detail-title')).toHaveText(
    'SACCO & lender records',
  )
  await page.locator('.evidence-source-detail summary').click()
  await expect(
    page.getByText(/A direct SACCO account integration is not connected/),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Step', exact: true }).click()
  await expect(
    page.getByText('Iteration 1 / 12', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Reset', exact: true }).click()
  await page
    .getByRole('button', { name: 'Play PageRank animation', exact: true })
    .click()
  await expect(
    page.getByText('Iteration 2 / 12', { exact: true }),
  ).toBeVisible()
  await page.locator('.product-intro').scrollIntoViewIfNeeded()
  await expect(
    page.getByRole('button', { name: 'Play PageRank animation', exact: true }),
  ).toBeAttached()
  await page.getByRole('button', { name: /Community patterns/ }).click()
  await expect(
    page.getByText('Community labels are authored, not computed.', {
      exact: true,
    }),
  ).toBeVisible()
  await page.getByLabel('Inspect a teaching node').selectOption('7')
  await expect(page.locator('.gds-selected-node')).toHaveText(
    'SACCO B: 3 outgoing and 5 incoming links.',
  )
  expect(apiRequests).toEqual([])
})

test('mobile evidence and graph controls preserve access with reduced motion', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/about')
  await page.getByLabel('Explore a payment stage').selectOption('6')
  await expect(page.locator('.payment-verdict')).toHaveText('Not recorded')
  await page.getByRole('button', { name: /Business cash flow/ }).click()
  await expect(page.locator('#source-detail-title')).toHaveText(
    'Business cash flow',
  )
  await page.getByRole('button', { name: /Community patterns/ }).click()
  await expect(
    page.getByRole('button', { name: 'Inspect Chama A', exact: true }),
  ).toHaveAttribute('transform', 'translate(280 100)')
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy()
})
