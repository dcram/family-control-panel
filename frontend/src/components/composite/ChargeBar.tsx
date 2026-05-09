import type { Child } from "@/types"

export interface ChildCharge {
  child: Child
  totalMinutes: number
}

interface ChargeBarProps {
  charges: ChildCharge[]
}

const COLOR_HEX: Record<string, string> = {
  green: "#14b8a6",
  blue: "#3b82f6",
  amber: "#f59e0b",
  coral: "#f97316",
  purple: "#8b5cf6",
  gray: "#9ca3af",
}

export function ChargeBar({ charges }: ChargeBarProps) {
  if (charges.length === 0) return null

  const totals = charges.map((c) => c.totalMinutes)
  const sum = totals.reduce((a, b) => a + b, 0)
  const average = charges.length > 0 ? sum / charges.length : 0

  function isUnbalanced(minutes: number): boolean {
    if (average === 0) return false
    return Math.abs(minutes - average) / average > 0.3
  }

  return (
    <div className="flex flex-wrap gap-3 px-4 py-2 border-b border-border text-sm">
      {charges.map(({ child, totalMinutes }) => (
        <span key={child.id} className="flex items-center gap-1.5">
          <span
            className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: COLOR_HEX[child.color] ?? "#9ca3af" }}
          />
          <span className="font-medium">{child.first_name}</span>
          <span
            className={
              isUnbalanced(totalMinutes)
                ? "text-amber-600 font-semibold"
                : "text-muted-foreground"
            }
          >
            {totalMinutes} min
          </span>
        </span>
      ))}
    </div>
  )
}
