import { useState } from "react"
import { PinPad } from "@/components/atomic/PinPad"
import { KioskBanner } from "@/components/composite/KioskBanner"
import { WeekGrid } from "@/components/composite/WeekGrid"
import { useKioskInfo } from "@/hooks/useKioskInfo"
import { useMoments } from "@/hooks/useMoments"
import { useInvalidateWeekPlanning, useWeekPlanning } from "@/hooks/useWeekPlanning"
import { addWeeks, currentMonday, toISODate } from "@/lib/dates"
import { buildDayData } from "@/lib/planning"
import type { TaskInstance } from "@/types"

export function KioskView() {
  const [weekStart, setWeekStart] = useState(currentMonday)
  const [selected, setSelected] = useState<TaskInstance | null>(null)

  const { data: info } = useKioskInfo()
  const { data: instances = [] } = useWeekPlanning(toISODate(weekStart))
  const { data: moments = [] } = useMoments()
  const invalidate = useInvalidateWeekPlanning()

  const nextWeek = addWeeks(currentMonday(), 1)
  const isAtMaxWeek = weekStart >= nextWeek

  const days = buildDayData(weekStart, instances, moments)
  const now = new Date()

  async function verifyPin(pin: string) {
    const res = await fetch("/api/v1/auth/verify-pin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin }),
    })
    if (!res.ok) return null
    return res.json() as Promise<{ holder_type: string; holder_id: string }>
  }

  async function handleDeclare(pin: string) {
    if (!selected) return
    await fetch(`/api/v1/instances/${selected.id}/declare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin }),
    })
    setSelected(null)
    void invalidate(toISODate(weekStart))
  }

  async function handleValidate(pin: string) {
    if (!selected) return
    await fetch(`/api/v1/instances/${selected.id}/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin, target_state: "done" }),
    })
    setSelected(null)
    void invalidate(toISODate(weekStart))
  }

  async function handleInvalidate(pin: string, reason: "refused" | "other") {
    if (!selected) return
    await fetch(`/api/v1/instances/${selected.id}/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin, target_state: "undone", reason }),
    })
    setSelected(null)
    void invalidate(toISODate(weekStart))
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <KioskBanner
        date={info?.date ? new Date(info.date) : now}
        saint={info?.saint ?? null}
        weather={info?.weather ?? null}
        quoteText={info?.quote_text ?? null}
        quoteAuthor={info?.quote_author ?? null}
      />

      {/* Navigation semaine */}
      <div className="flex items-center justify-center gap-3 py-2 border-b border-border">
        <button
          type="button"
          onClick={() => setWeekStart((w) => addWeeks(w, -1))}
          className="text-sm px-3 py-1 rounded-lg bg-muted hover:bg-muted/80"
        >
          ← Préc
        </button>
        <button
          type="button"
          onClick={() => setWeekStart(currentMonday())}
          className="text-sm px-3 py-1 rounded-lg bg-primary text-primary-foreground"
        >
          Aujourd'hui
        </button>
        <button
          type="button"
          onClick={() => setWeekStart((w) => addWeeks(w, 1))}
          disabled={isAtMaxWeek}
          className="text-sm px-3 py-1 rounded-lg bg-muted hover:bg-muted/80 disabled:opacity-40"
        >
          Suiv →
        </button>
      </div>

      <div className="flex-1 overflow-auto p-3">
        <WeekGrid
          days={days}
          mode="kiosk"
          now={now}
          onTaskTap={(id) => {
            const inst = instances.find((i) => i.id === id) ?? null
            setSelected(inst)
          }}
        />
      </div>

      {selected && (
        <PinPad
          taskLabel={selected.task_label}
          taskEmoji={selected.task_emoji}
          childFirstName={selected.child_first_name}
          childColor={selected.child_color}
          taskState={selected.state}
          onVerifyPin={verifyPin}
          onDeclare={(pin) => void handleDeclare(pin)}
          onValidate={(pin) => void handleValidate(pin)}
          onInvalidate={(pin, reason) => void handleInvalidate(pin, reason)}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  )
}
