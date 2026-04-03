/**
 * api.js
 * ------
 * All communication with the FastAPI backend.
 * Components never call fetch() directly — they use this module.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Request failed: ${response.status}`)
  }
  return response.json()
}

export async function fetchModsBySlot(slot) {
  const params = new URLSearchParams()
  if (slot) params.append('slot', slot)
  return request(`/mods?${params}`)
}

export async function fetchSlots() {
  return request('/mods/slots')
}

export async function generateRegex(modIds) {
  return request('/mods/regex', {
    method: 'POST',
    body: JSON.stringify({ mod_ids: modIds }),
  })
}
