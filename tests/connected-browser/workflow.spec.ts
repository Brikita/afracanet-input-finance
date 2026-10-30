import { test, expect } from '@playwright/test'
import path from 'node:path'

test('officer review reaches input finance through signed delivery and renders at three widths', async ({
  page,
  context,
}) => {
  const errors: string[] = []
  page.on('pageerror', (error) => {
    errors.push(error.message)
    console.log('Browser error:', error.message)
  })
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('http://127.0.0.1:15174/')
  await page.getByLabel('Officer account').fill('browser-officer')
  await page
    .getByLabel('Password', { exact: true })
    .fill('isolated-browser-password')
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await page.getByRole('button', { name: /farmer-synth-000001/ }).click()
  await page.getByRole('button', { name: 'Load graph context' }).click()
  await expect(
    page.getByText('Synthetic Farmer 000001', { exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole('heading', { name: 'Public weather at a reference point' }),
  ).toBeVisible()
  await page.getByLabel('Allocation in USD cents').fill('18000')
  await page.getByLabel('Expiry date (UTC)').fill('2027-01-30')
  await page
    .getByLabel('Decision reason', { exact: true })
    .fill('Officer reviewed this synthetic browser scenario.')
  await page.getByLabel(/I am authorized to record/).check()
  for (const [name, width, height] of [
    ['desktop', 1440, 900],
    ['tablet', 768, 1024],
    ['mobile', 390, 844],
  ] as const) {
    await page.setViewportSize({ width, height })
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy()
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.screenshot({
      path: path.resolve(`.impeccable/review/connected-credit-${name}.png`),
      fullPage: true,
    })
  }
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.getByRole('button', { name: 'Approve and queue handoff' }).click()
  await expect(
    page.getByRole('heading', { name: 'Recorded lender decision' }),
  ).toBeVisible()
  await expect(
    page.getByText('Approval · delivered', { exact: true }),
  ).toBeVisible({ timeout: 30000 })
  const destination = await page
    .getByRole('link', { name: 'Continue to input finance' })
    .getAttribute('href')
  expect(destination).toContain('approval=')
  const inputs = await context.newPage()
  await inputs.setViewportSize({ width: 1440, height: 900 })
  await inputs.goto(destination!)
  await inputs.getByRole('button', { name: 'Open workspace' }).click()
  await inputs.getByLabel('View as').selectOption('SYN-LENDER-000')
  await expect(
    inputs.getByText('Signed lender service', { exact: true }),
  ).toBeVisible()
  await expect(inputs.getByText('$180.00 USD', { exact: true })).toBeVisible()
  await inputs.evaluate(() => window.scrollTo(0, 0))
  await inputs.screenshot({
    path: path.resolve('.impeccable/review/connected-input-desktop.png'),
    fullPage: true,
  })
  await inputs.setViewportSize({ width: 390, height: 844 })
  expect(
    await inputs.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy()
  await inputs.evaluate(() => window.scrollTo(0, 0))
  await inputs.screenshot({
    path: path.resolve('.impeccable/review/connected-input-mobile.png'),
    fullPage: true,
  })
  const reviewRevocation = inputs.getByRole('button', {
    name: /^Review revocation for /,
  })
  await expect(reviewRevocation).toBeVisible()
  expect(
    await reviewRevocation.evaluate(
      (el) => el.getBoundingClientRect().right <= innerWidth,
    ),
  ).toBeTruthy()
  await reviewRevocation.click()
  await inputs
    .getByLabel(/^Reason for revoking /)
    .fill('Reviewing the full UUID reference on mobile.')
  const confirmRevocation = inputs.getByRole('button', {
    name: /^Revoke [a-f0-9-]{36}$/,
  })
  await expect(confirmRevocation).toBeVisible()
  expect(
    await confirmRevocation.evaluate(
      (el) => el.getBoundingClientRect().right <= innerWidth,
    ),
  ).toBeTruthy()
  await inputs.evaluate(() => window.scrollTo(0, 0))
  await inputs.screenshot({
    path: path.resolve('.impeccable/review/connected-input-confirm-mobile.png'),
    fullPage: true,
  })
  await inputs
    .getByRole('button', { name: 'Keep decision', exact: true })
    .click()
  await page
    .getByRole('textbox', { name: 'Revocation reason', exact: true })
    .fill('Withdraw this illustrative authorization.')
  await page.getByRole('button', { name: 'Revoke this approval' }).click()
  await expect(
    page.getByText('Revocation · delivered', { exact: true }),
  ).toBeVisible({ timeout: 30000 })
  await inputs.reload()
  await expect(inputs.getByText('Revoked', { exact: true })).toBeVisible()
  expect(errors).toEqual([])
})
