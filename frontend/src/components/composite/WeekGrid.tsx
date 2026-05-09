import type { MomentWithTasks } from "./DayColumn"
import { DayColumn } from "./DayColumn"

export interface DayData {
  date: Date
  moments: MomentWithTasks[]
}

interface WeekGridProps {
  days: DayData[]
  mode: "kiosk" | "admin"
  now: Date
  onTaskTap?: (instanceId: string) => void
  onTaskEdit?: (instanceId: string) => void
  onTaskDelete?: (instanceId: string) => void
  onTaskValidate?: (instanceId: string) => void
  onTaskInvalidate?: (instanceId: string) => void
  onTaskReset?: (instanceId: string) => void
  onAddTask?: (momentId: string, date: Date) => void
}

function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

export function WeekGrid({
  days,
  mode,
  now,
  onTaskTap,
  onTaskEdit,
  onTaskDelete,
  onTaskValidate,
  onTaskInvalidate,
  onTaskReset,
  onAddTask,
}: WeekGridProps) {
  return (
    <div className="grid grid-cols-7 gap-2 overflow-x-auto">
      {days.map(({ date, moments }) => (
        <DayColumn
          key={date.toISOString()}
          date={date}
          moments={moments}
          mode={mode}
          now={now}
          isToday={isSameDay(date, now)}
          onTaskTap={onTaskTap}
          onTaskEdit={onTaskEdit}
          onTaskDelete={onTaskDelete}
          onTaskValidate={onTaskValidate}
          onTaskInvalidate={onTaskInvalidate}
          onTaskReset={onTaskReset}
          onAddTask={onAddTask ? (momentId) => onAddTask(momentId, date) : undefined}
        />
      ))}
    </div>
  )
}
