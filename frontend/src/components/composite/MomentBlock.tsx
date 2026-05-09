import { IconPlus } from "@tabler/icons-react"
import { TaskCard } from "@/components/atomic/TaskCard"
import type { Moment, TaskInstance } from "@/types"

interface MomentBlockProps {
  moment: Moment
  tasks: TaskInstance[]
  mode: "kiosk" | "admin"
  now: Date
  onTaskTap?: (instanceId: string) => void
  onTaskEdit?: (instanceId: string) => void
  onTaskDelete?: (instanceId: string) => void
  onTaskValidate?: (instanceId: string) => void
  onTaskInvalidate?: (instanceId: string) => void
  onTaskReset?: (instanceId: string) => void
  onAddTask?: (momentId: string) => void
}

function isOverdue(instance: TaskInstance, moment: Moment, now: Date): boolean {
  if (["done", "undone", "unknown"].includes(instance.state)) return false
  const [hours, minutes] = moment.end_time.split(":").map(Number)
  const endTime = new Date(now)
  endTime.setHours(hours, minutes, 0, 0)
  return now > endTime
}

export function MomentBlock({
  moment,
  tasks,
  mode,
  now,
  onTaskTap,
  onTaskEdit,
  onTaskDelete,
  onTaskValidate,
  onTaskInvalidate,
  onTaskReset,
  onAddTask,
}: MomentBlockProps) {
  if (mode === "kiosk" && tasks.length === 0) return null

  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        {moment.label}
      </span>
      {tasks.map((instance) => (
        <TaskCard
          key={instance.id}
          instance={instance}
          mode={mode}
          overdue={isOverdue(instance, moment, now)}
          onTap={() => onTaskTap?.(instance.id)}
          onEdit={() => onTaskEdit?.(instance.id)}
          onDelete={() => onTaskDelete?.(instance.id)}
          onValidate={() => onTaskValidate?.(instance.id)}
          onInvalidate={() => onTaskInvalidate?.(instance.id)}
          onReset={() => onTaskReset?.(instance.id)}
        />
      ))}
      {mode === "admin" && (
        <button
          type="button"
          onClick={() => onAddTask?.(moment.id)}
          className="w-full border border-dashed border-muted-foreground/40 rounded-lg py-1.5 text-xs text-muted-foreground hover:border-primary hover:text-primary transition-colors flex items-center justify-center gap-1"
        >
          <IconPlus size={12} />
          Ajouter
        </button>
      )}
    </div>
  )
}
