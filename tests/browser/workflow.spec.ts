import { test, expect } from '@playwright/test'

test('lender reviews a mapped decision, explicitly authorizes it, and records revocation', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await page
    .getByRole('button', { name: 'Credit allocations', exact: true })
    .click()
  const expiry = new Date(Date.now() + 60 * 86400000)
  const approved = new Date(Date.now() - 10 * 60000)
  const localDate = (value: Date) => {
    const shifted = new Date(
      value.getTime() - value.getTimezoneOffset() * 60000,
    )
    return shifted.toISOString().slice(0, 16)
  }
  await page
    .getByLabel('Or paste approval CSV')
    .fill(
      `farmer_id,name,location,limit_cents,expires_at,approval_reference\nfarmer-handoff,Rehema Demo,Nakuru,4000,${expiry.toISOString()},PROFILE-HANDOFF`,
    )
  await page
    .getByRole('button', { name: 'Preview approvals', exact: true })
    .click()
  await page
    .getByRole('button', { name: 'Import 1 approval', exact: true })
    .click()
  await expect(page.getByText('1 approval(s) imported.')).toBeVisible()
  await page
    .getByLabel('Source farmer reference', { exact: true })
    .fill('F-UI-HANDOFF')
  await page
    .getByLabel('Farmer in input finance')
    .selectOption('farmer-handoff')
  await page.getByRole('button', { name: 'Confirm farmer mapping' }).click()
  await expect(
    page.getByText('Farmer mapping confirmed.', { exact: false }),
  ).toBeVisible()
  await page
    .getByRole('combobox', { name: 'Linked farmer', exact: true })
    .selectOption({ label: 'Rehema Demo · F-UI-HANDOFF' })
  await page
    .getByLabel('Source application reference', { exact: true })
    .fill('APP-UI-HANDOFF')
  await page
    .getByLabel('Lender decision reference', { exact: true })
    .fill('DECISION-UI-HANDOFF')
  await page.getByLabel('Officer recorded on decision').fill('officer-ui')
  await page.getByLabel('Total allocation (USD)', { exact: true }).fill('90.00')
  await page
    .getByLabel('Decision made', { exact: true })
    .fill(localDate(approved))
  await page
    .getByLabel('Allocation expiry', { exact: true })
    .fill(localDate(expiry))
  await page
    .getByRole('combobox', { name: 'Assessment data provenance', exact: true })
    .selectOption('synthetic')
  await page
    .getByRole('button', { name: 'Preview lender decision', exact: true })
    .click()
  const preview = page.getByLabel('Lender decision preview', { exact: true })
  await expect(preview.getByText('$90.00 USD', { exact: true })).toBeVisible()
  await expect(
    page.getByRole('button', { name: 'Authorize reviewed allocation' }),
  ).toBeDisabled()
  await page.screenshot({
    path: '.impeccable/review/handoff-desktop.png',
    fullPage: true,
  })
  for (const width of [768, 390]) {
    await page.setViewportSize({ width, height: 900 })
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true)
    await page.screenshot({
      path: `.impeccable/review/handoff-${width}.png`,
      fullPage: true,
    })
  }
  await preview.screenshot({
    path: '.impeccable/review/handoff-preview-mobile.png',
  })
  await page
    .getByLabel(
      'I have reviewed this lender decision and authorize this allocation.',
    )
    .check()
  await page
    .getByRole('button', { name: 'Authorize reviewed allocation' })
    .click()
  await expect(
    page.getByText('Lender-reviewed decision recorded.', { exact: false }),
  ).toBeVisible()
  const record = page
    .locator('.handoff-history-record')
    .filter({ hasText: 'DECISION-UI-HANDOFF' })
  await record.locator('summary').click()
  await expect(
    record.getByText('APP-UI-HANDOFF', { exact: true }),
  ).toBeVisible()
  await expect(
    record.getByText('Current allocation', { exact: true }),
  ).toBeVisible()
  await page.screenshot({
    path: '.impeccable/review/handoff-record-mobile.png',
    fullPage: true,
  })
  await record
    .getByRole('button', { name: 'Review revocation for DECISION-UI-HANDOFF' })
    .click()
  await record
    .getByLabel('Reason for revoking DECISION-UI-HANDOFF')
    .fill('Lender requires an updated decision.')
  await record
    .getByRole('button', { name: 'Revoke DECISION-UI-HANDOFF', exact: true })
    .click()
  await expect(record.getByText('Revoked', { exact: true })).toBeVisible()
  await record.screenshot({
    path: '.impeccable/review/handoff-revoked-mobile.png',
  })
  await page
    .getByText('Import a prepared decision file instead', { exact: true })
    .click()
  await page.getByLabel('Or paste lender decision JSON').fill('{broken')
  await page
    .getByRole('button', { name: 'Preview decision file', exact: true })
    .click()
  await expect(
    page.getByText('The decision file must contain valid JSON.'),
  ).toBeVisible()
  await page.getByLabel('View as').selectOption('farmer-handoff')
  await expect(
    page.getByText(
      'Your allocation has expired or been revoked. Contact your lender to renew it.',
    ),
  ).toBeVisible()
  await expect(
    page.getByRole('button', { name: 'Confirm input request' }),
  ).toBeDisabled()
})

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
  await page.getByRole('button', { name: 'My requests', exact: true }).click()
  await page.getByRole('button', { name: 'My inputs', exact: true }).click()
  await expect(
    page.getByLabel('Quantity for DAP fertilizer 50 kg bag'),
  ).toHaveValue('2')
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

test('lender imports an approval and dealer maintains catalogue on mobile', async ({
  page,
}) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await page
    .getByRole('button', { name: 'Credit allocations', exact: true })
    .click()
  const expiry = new Date(Date.now() + 60 * 86400000).toISOString()
  await page
    .getByLabel('Or paste approval CSV')
    .fill(
      `farmer_id,name,location,limit_cents,expires_at,approval_reference\nfarmer-browser,Jane Demo,Nakuru,4000,${expiry},BANK-BROWSER-01`,
    )
  await page.getByRole('button', { name: 'Preview approvals' }).click()
  await expect(
    page.getByRole('button', { name: 'Import 1 approval', exact: true }),
  ).toBeVisible()
  await page
    .getByRole('button', { name: 'Import 1 approval', exact: true })
    .click()
  await expect(page.getByText('1 approval(s) imported.')).toBeVisible()
  await page.getByLabel('View as').selectOption('supplier-demo')
  await page.getByRole('button', { name: 'Inventory', exact: true }).click()
  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: 'Add product', exact: true }).click()
  await page.getByLabel('Product ID', { exact: true }).fill('beans-browser')
  await page.getByLabel('Product name', { exact: true }).fill('Beans seed')
  await page.getByLabel('Category', { exact: true }).fill('Seed')
  await page.getByLabel('Unit / pack size', { exact: true }).fill('1 kg pack')
  await page.getByLabel('Unit price (USD)', { exact: true }).fill('8.50')
  await page.getByLabel('On-hand stock', { exact: true }).fill('20')
  await page.getByRole('button', { name: 'Save product', exact: true }).click()
  await expect(
    page.getByText('Catalogue saved. Existing order prices remain unchanged.'),
  ).toBeVisible()
  await page.screenshot({
    path: 'data/screenshots/inventory-management-mobile.png',
    fullPage: true,
  })
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true)
  await page.getByLabel('View as').selectOption('farmer-browser')
  await expect(
    page.getByRole('button', { name: 'Add Beans seed 1 kg pack' }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Add Beans seed 1 kg pack' }).click()
  await page.getByRole('button', { name: 'Confirm input request' }).click()
  await expect(
    page.getByRole('dialog').getByText('$8.50', { exact: false }).first(),
  ).toBeVisible()
  const reference = await page
    .getByRole('dialog')
    .getByRole('heading', { name: /^AFC-/ })
    .innerText()
  await page
    .getByRole('button', { name: 'Report an issue', exact: true })
    .click()
  await page
    .getByLabel('Describe the issue')
    .fill('Please confirm the seed batch before paying.')
  await page
    .getByRole('button', { name: 'Submit issue report', exact: true })
    .click()
  await expect(page.getByText('1 open issue.', { exact: false })).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByLabel('View as').selectOption('lender-demo')
  await page
    .getByRole('button', { name: 'Open ' + reference, exact: true })
    .click()
  await expect(
    page.getByRole('button', { name: 'Approve input order' }),
  ).toHaveCount(0)
  await page
    .getByLabel(/^Resolution for issue/)
    .fill('Supplier confirmed the batch with the farmer.')
  await page
    .getByRole('button', { name: 'Record issue resolution', exact: true })
    .click()
  await expect(
    page.getByRole('button', { name: 'Approve input order' }),
  ).toBeVisible()
  await page.screenshot({
    path: 'data/screenshots/issue-resolution-mobile.png',
    fullPage: true,
  })
  await page.getByRole('button', { name: 'Approve input order' }).click()
  await expect(
    page.getByRole('dialog').getByText('Ready to invoice', { exact: true }),
  ).toBeVisible()
})

test('farmer verifies an SMS number and previews a Swahili order update', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await page.getByRole('button', { name: 'Farmer experience' }).click()
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await page.getByLabel('View as').selectOption('farmer-kiptoo')
  await page.getByRole('button', { name: 'SMS updates', exact: true }).click()
  await page
    .getByLabel('Kenyan mobile number', { exact: true })
    .fill('+254700000002')
  await page.getByLabel('Message language', { exact: true }).selectOption('sw')
  await page.getByRole('checkbox', { name: /I control this number/ }).check()
  await page
    .getByRole('button', { name: 'Save SMS preferences', exact: true })
    .click()
  await page
    .getByRole('button', { name: 'Preview next queued SMS', exact: true })
    .click()
  const preview = await page.locator('.sms-preview').first().innerText()
  const code = preview.match(/\b([0-9]{6})\b/)?.[1]
  expect(code).toBeTruthy()
  await page.getByLabel('Phone verification code', { exact: true }).fill(code!)
  await page
    .getByRole('button', { name: 'Verify mobile number', exact: true })
    .click()
  await expect(
    page.getByText('Verified · updates enabled', { exact: false }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'My inputs', exact: true }).click()
  await page
    .getByRole('button', { name: 'Add Maize seed 2 kg pack', exact: true })
    .click()
  await page
    .getByRole('button', { name: 'Confirm input request', exact: true })
    .click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.getByRole('button', { name: 'Close transaction' }).click()
  await page.getByRole('button', { name: 'SMS updates', exact: true }).click()
  await page
    .getByRole('button', { name: 'Preview next queued SMS', exact: true })
    .click()
  await expect(
    page.locator('.sms-preview').filter({ hasText: 'ombi limepokelewa' }),
  ).toContainText('[DEMO]')
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true)
  await page.screenshot({
    path: 'data/screenshots/farmer-sms-mobile.png',
    fullPage: true,
  })
  await page.getByLabel('View as').selectOption('lender-demo')
  await expect(
    page.getByRole('button', { name: 'SMS updates', exact: true }),
  ).toHaveCount(0)
})

test('lender filters cases, respects issue holds, and closes details by keyboard', async ({
  page,
}) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Farmer experience' }).click()
  await page.getByRole('button', { name: 'Open workspace' }).click()
  await page
    .getByRole('button', { name: 'Add Maize seed 2 kg pack', exact: true })
    .click()
  await page
    .getByRole('button', { name: 'Confirm input request', exact: true })
    .click()
  const dialog = page.getByRole('dialog')
  const reference = await dialog.locator('.drawer-header h2').innerText()
  await page.keyboard.press('Escape')
  await expect(dialog).toHaveCount(0)
  await page.getByLabel('View as').selectOption('lender-demo')
  await page.getByLabel('Search input requests').fill(reference)
  await expect(page.locator('.queue-caption')).toContainText(
    '1 request in this view',
  )
  await page.getByLabel('Filter requests by status').selectOption('COLLECTED')
  await expect(
    page.getByText('No matching requests', { exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole('button', { name: 'Approve input order' }),
  ).toHaveCount(0)
  await page.getByLabel('Filter requests by status').selectOption('all')
  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: `Select ${reference}` }).focus()
  await page.keyboard.press('Enter')
  await expect(page.locator('.selected-record')).toBeFocused()
  await page.keyboard.press('Tab')
  expect(
    await page.evaluate(() =>
      Boolean(document.activeElement?.closest('.selected-record')),
    ),
  ).toBe(true)
  await expect(
    page
      .locator('.selected-record')
      .getByRole('button', { name: 'Approve input order' }),
  ).toBeVisible()
  await page.getByRole('button', { name: `Open ${reference}` }).click()
  await dialog.getByRole('button', { name: 'Report an issue' }).click()
  await dialog
    .getByLabel('Describe the issue')
    .fill('Please verify the quoted input pack before approval.')
  await dialog.getByRole('button', { name: 'Submit issue report' }).click()
  await expect(dialog.getByText('1 open issue', { exact: false })).toBeVisible()
  await page.keyboard.press('Tab')
  expect(
    await page.evaluate(() =>
      Boolean(document.activeElement?.closest('[role="dialog"]')),
    ),
  ).toBe(true)
  await page.keyboard.press('Escape')
  await expect(
    page
      .locator('.selected-record')
      .getByRole('button', { name: 'Review order issue' }),
  ).toBeVisible()
  await expect(
    page.getByRole('button', { name: 'Approve input order' }),
  ).toHaveCount(0)
  for (const width of [1440, 768, 390]) {
    await page.setViewportSize({ width, height: 900 })
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true)
    await expect(
      page.getByRole('img', {
        name: /Available:.*Reserved:.*Paid to suppliers:/,
      }),
    ).toBeVisible()
  }
})
