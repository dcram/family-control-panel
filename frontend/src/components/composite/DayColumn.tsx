import { cn } from "@/lib/utils"
import { DAY_LABELS } from "@/lib/constants"
import type { Moment, TaskInstance } from "@/types"
import { MomentBlock } from "./MomentBlock"

export interface MomentWithTasks {
  moment: Moment
  tasks: TaskInstance[]
}

interface DayColumnProps {
  date: Date
  moments: MomentWithTasks[]
  mode: "kiosk" | "admin"
  now: Date
  isToday?: boolean
  onTaskTap?: (instanceId: string) => void
  onTaskEdit?: (instanceId: string) => void
  onTaskDelete?: (instanceId: string) => void
  onTaskValidate?: (instanceId: string) => void
  onTaskInvalidate?: (instanceId: string) => void
  onTaskReset?: (instanceId: string) => void
  onAddTask?: (momentId: string) => void
}

export function DayColumn({
  date,
  moments,
  mode,
  now,
  isToday = false,
  onTaskTap,
  onTaskEdit,
  onTaskDelete,
  onTaskValidate,
  onTaskInvalidate,
  onTaskReset,
  onAddTask,
}: DayColumnProps) {
  const dayLabel = DAY_LABELS[date.getDay() === 0 ? 6 : date.getDay() - 1]
  const dayNum = date.getDate()

  return (
    <div
      className={cn(
        "flex flex-col gap-2 p-2 rounded-lg border min-h-32",
        isToday ? "border-primary border-2 bg-secondary/30" : "border-border/50",
      )}
    >
      <div className="text-center">
        <span className="text-xs font-semibold text-muted-foreground">
          {dayLabel} {dayNum}
        </span>
        {isToday && (
          <span className="ml-1 text-[10px] bg-primary text-primary-foreground rounded px-1 py-0.5">
            auj.
          </span>
        )}
      </div>
      {moments.map(({ moment, tasks }) => (
        <MomentBlock
          key={moment.id}
          moment={moment}
          tasks={tasks}
          mode={mode}
          now={now}
          onTaskTap={onTaskTap}
          onTaskEdit={onTaskEdit}
          onTaskDelete={onTaskDelete}
          onTaskValidate={onTaskValidate}
          onTaskInvalidate={onTaskInvalidate}
          onTaskReset={onTaskReset}
          onAddTask={onAddTask}
        />
      ))}
    </div>
  )
}
