export function generateEndpointName(query: string): string {
  return (
    query
      .toLowerCase()
      .trim()
      // Remove apostrophes completely
      .replace(/'/g, '')
      // Replace other non-alphanumeric characters with hyphens
      .replace(/[^a-z0-9]+/g, '-')
      // Remove leading/trailing hyphens
      .replace(/^-+|-+$/g, '')
      .substring(0, 20)
      // Remove trailing hyphen if substring cut in middle of word
      .replace(/-+$/, '')
  )
}

export function generateUniqueEndpointName(query: string): string {
  const baseEndpoint = generateEndpointName(query)
  const timestamp = Date.now().toString(36)

  return `${baseEndpoint}-${timestamp}`
}
