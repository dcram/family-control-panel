import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { AdminSidebar } from "@/components/composite/AdminSidebar"
import { useInvalidateTasks, useTasks } from "@/hooks/useTasks"
import type { Task } from "@/types"

export function CatalogView() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { data: tasks = [] } = useTasks()
  const invalidate = useInvalidateTasks()

  const [form, setForm] = useState<{
    label: string
    emoji: string
    min_age: number
    duration_minutes: number
  } | null>(null)
  const [editing, setEditing] = useState<Task | null>(null)

  async function logout() {
    await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include" })
    await qc.invalidateQueries({ queryKey: ["me"] })
    navigate("/login")
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    if (!form) return
    const body = { ...form, emoji: form.emoji || null }
    if (editing) {
      await fetch(`/api/v1/tasks/${editing.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body),
      })
    } else {
      await fetch("/api/v1/tasks/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body),
      })
    }
    setForm(null)
    setEditing(null)
    invalidate()
  }

  async function handleArchive(task: Task) {
    if (!confirm(`Archiver « ${task.label} » ?`)) return
    await fetch(`/api/v1/tasks/${task.id}`, { method: "DELETE", credentials: "include" })
    invalidate()
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <AdminSidebar
        activeSection="catalog"
        onNavigate={(s) => navigate(`/${s}`)}
        onLogout={() => void logout()}
      />
      <div className="flex-1 overflow-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold">Catalogue de tâches</h1>
          {!form && (
            <button
              type="button"
              onClick={() => { setEditing(null); setForm({ label: "", emoji: "", min_age: 4, duration_minutes: 15 }) }}
              className="text-sm px-3 py-1.5 rounded-lg bg-primary text-primary-foreground"
            >
              + Ajouter
            </button>
          )}
        </div>

        {form && (
          <form onSubmit={(e) => void handleSave(e)} className="bg-card border border-border rounded-xl p-4 mb-4 flex flex-col gap-3">
            <h2 className="font-semibold text-sm">{editing ? "Modifier" : "Nouvelle tâche"}</h2>
            <div className="flex gap-2">
              <input
                className="border border-border rounded-lg px-3 py-2 text-sm w-16"
                placeholder="🧹"
                value={form.emoji}
                onChange={(e) => setForm((f) => f && { ...f, emoji: e.target.value })}
                maxLength={2}
              />
              <input
                className="border border-border rounded-lg px-3 py-2 text-sm flex-1"
                placeholder="Libellé"
                value={form.label}
                onChange={(e) => setForm((f) => f && { ...f, label: e.target.value })}
                required
              />
            </div>
            <div className="flex gap-2">
              <label className="flex flex-col gap-1 flex-1 text-xs text-muted-foreground">
                Âge min.
                <input
                  type="number" min={0} max={18}
                  className="border border-border rounded-lg px-3 py-2 text-sm"
                  value={form.min_age}
                  onChange={(e) => setForm((f) => f && { ...f, min_age: Number(e.target.value) })}
                />
              </label>
              <label className="flex flex-col gap-1 flex-1 text-xs text-muted-foreground">
                Durée (min)
                <input
                  type="number" min={1}
                  className="border border-border rounded-lg px-3 py-2 text-sm"
                  value={form.duration_minutes}
                  onChange={(e) => setForm((f) => f && { ...f, duration_minutes: Number(e.target.value) })}
                />
              </label>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="flex-1 py-2 rounded-lg bg-primary text-primary-foreground text-sm">
                {editing ? "Enregistrer" : "Créer"}
              </button>
              <button type="button" onClick={() => { setForm(null); setEditing(null) }} className="flex-1 py-2 rounded-lg bg-muted text-sm">
                Annuler
              </button>
            </div>
          </form>
        )}

        <div className="flex flex-col gap-2">
          {tasks.map((task) => (
            <div key={task.id} className="bg-card border border-border rounded-xl p-3 flex items-center gap-3">
              <span className="text-xl w-8 text-center">{task.emoji ?? "✓"}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{task.label}</p>
                <p className="text-xs text-muted-foreground">{task.min_age}+ ans · {task.duration_minutes} min</p>
              </div>
              <button type="button" onClick={() => { setEditing(task); setForm({ label: task.label, emoji: task.emoji ?? "", min_age: task.min_age, duration_minutes: task.duration_minutes }) }} className="text-xs px-2 py-1 rounded bg-muted hover:bg-muted/80">Modifier</button>
              <button type="button" onClick={() => void handleArchive(task)} className="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100">Archiver</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
