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
        name: 'Connect the records. See the whole story.',
      }),
    ).toBeVisible()
    await expect(
      page.getByText('Demonstration handover recorded', { exact: true }),
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
  await expect(page.locator('.payment-verdict')).toHaveText(
    'Verified in the check',
  )
  await page.getByRole('link', { name: 'Evidence', exact: true }).click()
  await page.getByRole('button', { name: /SACCO & lender records/ }).click()
  await expect(page.locator('#source-detail-title')).toHaveText(
    'SACCO & lender records',
  )
  await page.locator('.evidence-source-detail summary').click()
  await expect(
    page.getByText(/A direct SACCO account integration is not connected/),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Reset', exact: true }).click()
  await page.getByRole('button', { name: 'Step', exact: true }).click()
  await expect(
    page.getByText('Iteration 1 / 12', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Reset', exact: true }).click()
  await page
    .getByRole('button', { name: 'Resume graph tour', exact: true })
    .click()
  await expect(
    page.getByText('Iteration 2 / 12', { exact: true }),
  ).toBeVisible()
  await page.locator('.aether-hero').scrollIntoViewIfNeeded()
  const stopped = await page.locator('.gds-playback > span').innerText()
  await page.waitForTimeout(1100)
  await expect(page.locator('.gds-playback > span')).toHaveText(stopped)
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
  await expect(page.locator('.payment-verdict')).toHaveText(
    'Verified in the check',
  )
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

test('automatic tours enter view, continue from manual choices, and pause', async ({
  page,
}) => {
  await page.clock.install()
  const calls: string[] = []
  page.on('request', (r) => {
    if (new URL(r.url()).pathname.startsWith('/api/')) calls.push(r.url())
  })
  await page.goto('/about')
  await page
    .getByRole('button', { name: 'Pause hero background', exact: true })
    .click()
  await page.locator('.payment-proof-section').scrollIntoViewIfNeeded()
  await expect(
    page.getByRole('button', {
      name: 'Pause payment walkthrough',
      exact: true,
    }),
  ).toBeVisible()
  await page.clock.runFor(10200)
  await expect(page.locator('.payment-focus-position')).toHaveText(
    'Stage 2 of 7',
  )
  await page
    .getByRole('button', { name: '4 Payment verified', exact: true })
    .click()
  await page.clock.runFor(10200)
  await expect(page.locator('.payment-focus-position')).toHaveText(
    'Stage 5 of 7',
  )
  await page
    .getByRole('button', { name: 'Pause payment walkthrough', exact: true })
    .click()
  await page.clock.runFor(10500)
  await expect(page.locator('.payment-focus-position')).toHaveText(
    'Stage 5 of 7',
  )
  await page.locator('.evidence-map').scrollIntoViewIfNeeded()
  await page.clock.runFor(9300)
  await expect(page.locator('#source-detail-title')).toHaveText(
    'SACCO & lender records',
  )
  await page.locator('.evidence-source-detail summary').click()
  await expect(
    page.getByRole('button', { name: 'Resume evidence tour', exact: true }),
  ).toBeAttached()
  await page.locator('.gds-canvas').scrollIntoViewIfNeeded()
  await page.clock.runFor(16000)
  await expect(
    page.getByRole('button', { name: /Community patterns/ }),
  ).toHaveAttribute('aria-pressed', 'true')
  expect(calls).toEqual([])
})

test('public typography and photographs load, and reduced motion waits for opt-in', async ({
  page,
}) => {
  await page.clock.install()
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/about.html')
  await page.evaluate(() => document.fonts.ready)
  expect(
    await page.locator('h1').evaluate((e) => getComputedStyle(e).fontFamily),
  ).toContain('Bricolage Grotesque Variable')
  expect(
    await page
      .locator('.product-page')
      .evaluate((e) => getComputedStyle(e).fontFamily),
  ).toContain('Hanken Grotesk Variable')
  const photos = page.locator('.scroll-reveal-image img')
  await expect(photos).toHaveCount(3)
  for (const photo of await photos.all()) {
    await photo.scrollIntoViewIfNeeded()
    await expect
      .poll(() =>
        photo.evaluate(
          (e: HTMLImageElement) => e.complete && e.naturalWidth > 1000,
        ),
      )
      .toBeTruthy()
  }
  await page.locator('.payment-proof-section').scrollIntoViewIfNeeded()
  await page.clock.runFor(12000)
  await expect(page.locator('.payment-focus-position')).toHaveText(
    'Stage 1 of 7',
  )
  await page
    .getByRole('button', { name: 'Resume payment walkthrough', exact: true })
    .click()
  await page.clock.runFor(10200)
  await expect(page.locator('.payment-focus-position')).toHaveText(
    'Stage 2 of 7',
  )
})
