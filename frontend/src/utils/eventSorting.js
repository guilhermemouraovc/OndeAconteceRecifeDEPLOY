export function sortEventsByPriorityAndDate(events) {
  if (!events || events.length === 0) return events

  return [...events].sort((a, b) => {
    const aPriority = a.display_priority ?? null
    const bPriority = b.display_priority ?? null
    const aDate = a.start_date ? new Date(a.start_date).getTime() : Infinity
    const bDate = b.start_date ? new Date(b.start_date).getTime() : Infinity

    if (aPriority !== null && bPriority !== null) {
      if (aPriority !== bPriority) return aPriority - bPriority
      return aDate - bDate
    }
    if (aPriority !== null) return -1
    if (bPriority !== null) return 1
    return aDate - bDate
  })
}
