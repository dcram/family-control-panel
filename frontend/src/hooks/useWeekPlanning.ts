import { useQuery, useQueryClient } from "@tanstack/react-query"
import type { WeekPlanning } from "@/types"

async function fetchWeekPlanning(weekStart: string, isAdmin: boolean): Promise<WeekPlanning> {
  const url = isAdmin
    ? `/api/v1/instances/week/${weekStart}`
    : `/api/v1/kiosk/week/${weekStart}`
  const res = await fetch(url, { credentials: "include" })
  if (!res.ok) throw new Error(`Erreur ${res.status}`)
  return res.json() as Promise<WeekPlanning>
}

export function useWeekPlanning(weekStart: string, isAdmin = false) {
  return useQuery({
    queryKey: ["planning", weekStart, isAdmin],
    queryFn: () => fetchWeekPlanning(weekStart, isAdmin),
    enabled: Boolean(weekStart),
  })
}

export function useInvalidateWeekPlanning() {
  const queryClient = useQueryClient()
  return (weekStart: string) =>
    queryClient.invalidateQueries({ queryKey: ["planning", weekStart] })
}
