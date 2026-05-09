import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { AdminSidebar } from "@/components/composite/AdminSidebar"
import { useChildren, useInvalidateChildren } from "@/hooks/useChildren"
import type { Child } from "@/types"

function age(dob: string): number {
  const today = new Date()
  const birth = new Date(dob)
  let a = today.getFullYear() - birth.getFullYear()
  if (
    today.getMonth() < birth.getMonth() ||
    (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate())
  ) a--
  return a
}

export function ChildrenView() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { data: children = [] } = useChildren()
  const invalidate = useInvalidateChildren()

  const [form, setForm] = useState<{ first_name: string; date_of_birth: string } | null>(null)
  const [editing, setEditing] = useState<Child | null>(null)

  async function logout() {
    await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include" })
    await qc.invalidateQueries({ queryKey: ["me"] })
    navigate("/login")
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!form) return
    await fetch("/api/v1/children/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(form),
    })
    setForm(null)
    invalidate()
  }

  async function handleUpdate(e: React.FormEvent) {
    e.preventDefault()
    if (!editing || !form) return
    await fetch(`/api/v1/children/${editing.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(form),
    })
    setEditing(null)
    setForm(null)
    invalidate()
  }

  async function handleArchive(child: Child) {
    if (!confirm(`Archiver ${child.first_name} ?`)) return
    await fetch(`/api/v1/children/${child.id}`, {
      method: "DELETE",
      credentials: "include",
    })
    invalidate()
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <AdminSidebar
        activeSection="children"
        onNavigate={(s) => navigate(`/${s}`)}
        onLogout={() => void logout()}
      />
      <div className="flex-1 overflow-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold">Enfants</h1>
          {!form && (
            <button
              type="button"
              onClick={() => { setEditing(null); setForm({ first_name: "", date_of_birth: "" }) }}
              className="text-sm px-3 py-1.5 rounded-lg bg-primary text-primary-foreground"
            >
              + Ajouter
            </button>
          )}
        </div>

        {form && (
          <form
            onSubmit={(e) => void (editing ? handleUpdate(e) : handleCreate(e))}
            className="bg-card border border-border rounded-xl p-4 mb-4 flex flex-col gap-3"
          >
            <h2 className="font-semibold text-sm">
              {editing ? `Modifier ${editing.first_name}` : "Nouvel enfant"}
            </h2>
            <input
              className="border border-border rounded-lg px-3 py-2 text-sm"
              placeholder="Prénom"
              value={form.first_name}
              onChange={(e) => setForm((f) => f && { ...f, first_name: e.target.value })}
              required
            />
            <input
              type="date"
              className="border border-border rounded-lg px-3 py-2 text-sm"
              value={form.date_of_birth}
              onChange={(e) => setForm((f) => f && { ...f, date_of_birth: e.target.value })}
              required
            />
            <div className="flex gap-2">
              <button type="submit" className="flex-1 py-2 rounded-lg bg-primary text-primary-foreground text-sm">
                {editing ? "Enregistrer" : "Créer"}
              </button>
              <button
                type="button"
                onClick={() => { setForm(null); setEditing(null) }}
                className="flex-1 py-2 rounded-lg bg-muted text-sm"
              >
                Annuler
              </button>
            </div>
          </form>
        )}

        <div className="flex flex-col gap-2">
          {children.map((child) => (
            <div key={child.id} className="bg-card border border-border rounded-xl p-4 flex items-center gap-3">
              <span className="text-sm font-semibold flex-1">
                {child.first_name}
                <span className="ml-2 text-muted-foreground font-normal text-xs">
                  {age(child.date_of_birth)} ans
                </span>
              </span>
              <button
                type="button"
                onClick={() => { setEditing(child); setForm({ first_name: child.first_name, date_of_birth: child.date_of_birth }) }}
                className="text-xs px-2 py-1 rounded bg-muted hover:bg-muted/80"
              >
                Modifier
              </button>
              <button
                type="button"
                onClick={() => void handleArchive(child)}
                className="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100"
              >
                Archiver
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
