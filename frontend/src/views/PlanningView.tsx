import { useState } from "react"
import { AdminSidebar } from "@/components/composite/AdminSidebar"
import { ChargeBar, type ChildCharge } from "@/components/composite/ChargeBar"
import { WeekGrid } from "@/components/composite/WeekGrid"
import { useChildren } from "@/hooks/useChildren"
import { useMoments } from "@/hooks/useMoments"
import { useInvalidateWeekPlanning, useWeekPlanning } from "@/hooks/useWeekPlanning"
import { addWeeks, currentMonday, toISODate } from "@/lib/dates"
import { buildDayData } from "@/lib/planning"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"

export function PlanningView() {
  const [weekStart, setWeekStart] = useState(currentMonday)
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: instances = [] } = useWeekPlanning(toISODate(weekStart), true)
  const { data: moments = [] } = useMoments()
  const { data: children = [] } = useChildren()
  const invalidate = useInvalidateWeekPlanning()

  const days = buildDayData(weekStart, instances, moments)
  const now = new Date()

  const nextWeek = addWeeks(currentMonday(), 1)
  const isAtMaxWeek = weekStart >= nextWeek

  const charges: ChildCharge[] = children.map((child) => ({
    child,
    totalMinutes: instances
      .filter((i) => i.child_first_name === child.first_name)
      .reduce((sum, i) => sum + i.task_duration_minutes, 0),
  }))

  async function callInstance(id: string, action: string, body: object) {
    await fetch(`/api/v1/instances/${id}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    })
    void invalidate(toISODate(weekStart))
  }

  async function logout() {
    await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include" })
    await qc.invalidateQueries({ queryKey: ["me"] })
    navigate("/login")
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <AdminSidebar
        activeSection="planning"
        onNavigate={(s) => navigate(`/${s}`)}
        onLogout={() => void logout()}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-2 border-b border-border">
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
          <span className="text-sm text-muted-foreground ml-auto">
            Semaine du {toISODate(weekStart)}
          </span>
        </div>
        <ChargeBar charges={charges} />
        <div className="flex-1 overflow-auto p-3">
          <WeekGrid
            days={days}
            mode="admin"
            now={now}
            onTaskValidate={(id) =>
              void callInstance(id, "validate", { target_state: "done" })
            }
            onTaskInvalidate={(id) =>
              void callInstance(id, "validate", {
                target_state: "undone",
                reason: "other",
              })
            }
            onTaskReset={(id) => void callInstance(id, "reset", {})}
            onTaskDelete={async (id) => {
              const inst = instances.find((i) => i.id === id)
              if (!inst?.assignment_id) return
              await fetch(`/api/v1/assignments/${inst.assignment_id}`, {
                method: "DELETE",
                credentials: "include",
              })
              void invalidate(toISODate(weekStart))
            }}
          />
        </div>
      </div>
    </div>
  )
}
