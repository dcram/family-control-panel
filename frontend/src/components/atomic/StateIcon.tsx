import {
  IconAlertTriangle,
  IconCheck,
  IconQuestionMark,
  IconX,
} from "@tabler/icons-react"
import type { TaskState } from "@/types"

interface StateIconProps {
  state: TaskState
  overdue?: boolean
}

export function StateIcon({ state, overdue = false }: StateIconProps) {
  const size = 14

  if (state === "assigned") {
    if (!overdue) return null
    return <IconAlertTriangle size={size} className="text-amber-500" />
  }

  if (state === "declared") {
    return (
      <span className="inline-flex items-center gap-0.5">
        <IconCheck size={size} className="text-muted-foreground" />
        {overdue && <IconAlertTriangle size={size} className="text-amber-500" />}
      </span>
    )
  }

  if (state === "done") {
    return <IconCheck size={size} className="text-green-500" />
  }

  if (state === "undone") {
    return <IconX size={size} className="text-red-500" />
  }

  // unknown
  return <IconQuestionMark size={size} className="text-muted-foreground" />
}
