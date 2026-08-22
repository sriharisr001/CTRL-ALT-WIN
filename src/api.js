/** Parse API responses defensively, including plain-text FastAPI/proxy failures. */
export async function readApiResponse(response) {
  const raw = await response.text()
  let data = null
  if (raw) {
    try {
      data = JSON.parse(raw)
    } catch {
      console.error('SatyaFin API returned non-JSON:', { status: response.status, body: raw })
    }
  }
  if (!response.ok) {
    const detail = data?.detail || data?.message || (raw ? `Server error (${response.status}): ${raw.slice(0, 160)}` : `Request failed (${response.status})`)
    throw new Error(detail)
  }
  if (!data) {
    console.error('SatyaFin API returned an invalid success response:', { status: response.status, body: raw })
    throw new Error('The server returned an invalid response. Please try again.')
  }
  return data
}
