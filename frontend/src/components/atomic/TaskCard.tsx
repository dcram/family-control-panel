import { IconChecklist, IconTrash } from "@tabler/icons-react"
import { cn } from "@/lib/utils"
import type { TaskInstance } from "@/types"
import { ChildBadge } from "./ChildBadge"
import { StateIcon } from "./StateIcon"

interface TaskCardProps {
  instance: TaskInstance
  mode: "kiosk" | "admin"
  overdue?: boolean
  onTap?: () => void
  onValidate?: () => void
  onInvalidate?: () => void
  onReset?: () => void
  onDelete?: () => void
  onEdit?: () => void
}

const FINAL_STATES = new Set(["done", "undone", "unknown"])
const RESET_STATES = new Set(["declared", "done", "undone", "unknown"])

export function TaskCard({
  instance,
  mode,
  overdue = false,
  onTap,
  onValidate,
  onInvalidate,
  onReset,
  onDelete,
  onEdit,
}: TaskCardProps) {
  const isFinal = FINAL_STATES.has(instance.state)
  const isKiosk = mode === "kiosk"

  const tappable =
    isKiosk && (instance.state === "assigned" || instance.state === "declared")

  const borderClass =
    overdue && !isFinal
      ? "border-amber-400 border-2"
      : instance.state === "declared"
        ? "border-primary border-2"
        : "border-border"

  const opacityClass =
    instance.state === "done" || instance.state === "undone"
      ? "opacity-70"
      : instance.state === "unknown"
        ? "opacity-50"
        : ""

  function handleClick() {
    if (isKiosk && tappable) onTap?.()
    else if (!isKiosk) onEdit?.()
  }

  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-2 text-card-foreground shadow-sm",
        borderClass,
        opacityClass,
        tappable || (!isKiosk && onEdit) ? "cursor-pointer active:scale-95 transition-transform" : "",
      )}
      onClick={handleClick}
    >
      <div className="flex items-start gap-2">
        {/* Emoji ou icône générique */}
        <span className="text-lg leading-none flex-shrink-0">
          {instance.task_emoji ?? <IconChecklist size={20} className="text-muted-foreground" />}
        </span>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium leading-tight truncate">{instance.task_label}</p>
          <div className="mt-1 flex items-center justify-between gap-1">
            <ChildBadge firstName={instance.child_first_name} color={instance.child_color} />
            <div className="flex items-center gap-1">
              <StateIcon state={instance.state} overdue={overdue} />
              {!isKiosk && onDelete && (
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); onDelete() }}
                  className="text-muted-foreground hover:text-destructive transition-colors"
                  aria-label="Supprimer"
                >
                  <IconTrash size={13} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Actions admin */}
      {!isKiosk && (
        <div className="mt-2 flex flex-wrap gap-1">
          {instance.state === "declared" && (
            <>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); onValidate?.() }}
                className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700 hover:bg-green-200"
              >
                Valider
              </button>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); onInvalidate?.() }}
                className="text-xs px-2 py-0.5 rounded bg-red-100 text-red-700 hover:bg-red-200"
              >
                Invalider
              </button>
            </>
          )}
          {RESET_STATES.has(instance.state) && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onReset?.() }}
              className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground hover:bg-muted/80"
            >
              Réinitialiser
            </button>
          )}
        </div>
      )}
    </div>
  )
}
