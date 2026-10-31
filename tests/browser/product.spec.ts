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
