export async function api<T>(
  path: string,
  token?: string,
  body?: unknown,
  method?: string,
): Promise<T> {
  const response = await fetch('/api' + path, {
    method: method ?? (body === undefined ? 'GET' : 'POST'),
    headers: {
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: 'Bearer ' + token } : {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  })
  if (!response.ok) {
    const result = await response.json().catch(() => ({}))
    throw new Error(
      typeof result.detail === 'string'
        ? result.detail
        : 'This request could not be completed.',
    )
  }
  return response.json() as Promise<T>
}
