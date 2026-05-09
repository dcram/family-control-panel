import type { DayData } from "@/components/composite/WeekGrid"
import type { Moment, TaskInstance } from "@/types"

export function buildDayData(
  weekStart: Date,
  instances: TaskInstance[],
  moments: Moment[],
): DayData[] {
  const sorted = [...moments].sort((a, b) => a.sort_order - b.sort_order)
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(weekStart)
    date.setDate(date.getDate() + i)
    const dayInstances = instances.filter((inst) => inst.day_of_week === i)
    return {
      date,
      moments: sorted.map((moment) => ({
        moment,
        tasks: dayInstances.filter((inst) => inst.moment_label === moment.label),
      })),
    }
  })
}

export function computeCharges(instances: TaskInstance[]) {
  const map = new Map<string, { firstName: string; color: string; minutes: number }>()
  for (const inst of instances) {
    const existing = map.get(inst.child_first_name)
    if (existing) {
      existing.minutes += inst.task_duration_minutes
    } else {
      map.set(inst.child_first_name, {
        firstName: inst.child_first_name,
        color: inst.child_color,
        minutes: inst.task_duration_minutes,
      })
    }
  }
  return map
}
