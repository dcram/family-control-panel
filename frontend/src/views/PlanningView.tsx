import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { AdminSidebar } from "@/components/composite/AdminSidebar"
import { ChargeBar, type ChildCharge } from "@/components/composite/ChargeBar"
import { WeekGrid } from "@/components/composite/WeekGrid"
import { useChildren } from "@/hooks/useChildren"
import { useMoments } from "@/hooks/useMoments"
import { useInvalidateWeekPlanning, useWeekPlanning } from "@/hooks/useWeekPlanning"
import { useTasks } from "@/hooks/useTasks"
import { addWeeks, currentMonday, toISODate } from "@/lib/dates"
import { buildDayData } from "@/lib/planning"
import type { Moment } from "@/types"
import { DAY_LABELS } from "@/lib/constants"

interface AddingState {
  momentId: string
  date: Date
  moment: Moment | undefined
}

function dayOfWeek(date: Date): number {
  const d = date.getDay()
  return d === 0 ? 6 : d - 1
}

export function PlanningView() {
  const [weekStart, setWeekStart] = useState(currentMonday)
  const [adding, setAdding] = useState<AddingState | null>(null)
  const [newTaskId, setNewTaskId] = useState("")
  const [newChildId, setNewChildId] = useState("")
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: instances = [] } = useWeekPlanning(toISODate(weekStart), true)
  const { data: moments = [] } = useMoments()
  const { data: children = [] } = useChildren()
  const { data: tasks = [] } = useTasks()
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

  async function handleAddAssignment(e: React.FormEvent) {
    e.preventDefault()
    if (!adding || !newTaskId || !newChildId) return
    await fetch("/api/v1/assignments/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        task_id: newTaskId,
        child_id: newChildId,
        moment_id: adding.momentId,
        day_of_week: dayOfWeek(adding.date),
      }),
    })
    setAdding(null)
    setNewTaskId("")
    setNewChildId("")
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
        {/* En-tête navigation semaine */}
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
              void callInstance(id, "validate", { target_state: "undone", reason: "other" })
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
            onAddTask={(momentId, date) => {
              setAdding({
                momentId,
                date,
                moment: moments.find((m) => m.id === momentId),
              })
              setNewTaskId("")
              setNewChildId("")
            }}
          />
        </div>
      </div>

      {/* Modal création assignation */}
      {adding && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={() => setAdding(null)}
        >
          <div
            className="bg-card border border-border rounded-2xl shadow-xl p-6 w-80 flex flex-col gap-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div>
              <h2 className="font-semibold">Nouvelle tâche</h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                {DAY_LABELS[dayOfWeek(adding.date)]} {adding.date.getDate()} —{" "}
                {adding.moment?.label ?? ""}
              </p>
            </div>
            <form onSubmit={(e) => void handleAddAssignment(e)} className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-muted-foreground">Tâche</label>
                <select
                  className="border border-border rounded-lg px-3 py-2 text-sm bg-background"
                  value={newTaskId}
                  onChange={(e) => setNewTaskId(e.target.value)}
                  required
                >
                  <option value="">Choisir une tâche…</option>
                  {tasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.emoji} {t.label} ({t.duration_minutes} min)
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-muted-foreground">Enfant</label>
                <select
                  className="border border-border rounded-lg px-3 py-2 text-sm bg-background"
                  value={newChildId}
                  onChange={(e) => setNewChildId(e.target.value)}
                  required
                >
                  <option value="">Choisir un enfant…</option>
                  {children.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.first_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2 mt-1">
                <button
                  type="submit"
                  className="flex-1 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-semibold"
                >
                  Assigner
                </button>
                <button
                  type="button"
                  onClick={() => setAdding(null)}
                  className="flex-1 py-2 rounded-xl bg-muted text-sm"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
