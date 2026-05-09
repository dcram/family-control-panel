import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"

export function LoginView() {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const qc = useQueryClient()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ login, password }),
      })
      if (!res.ok) {
        setError("Identifiants invalides")
        return
      }
      await qc.invalidateQueries({ queryKey: ["me"] })
      navigate("/planning")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-sm bg-card border border-border rounded-2xl p-8 shadow-sm">
        <h1 className="text-2xl font-bold mb-6 text-center">Administration</h1>
        <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium" htmlFor="login">
              Identifiant
            </label>
            <input
              id="login"
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              className="border border-border rounded-lg px-3 py-2 text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              autoComplete="username"
              required
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium" htmlFor="password">
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border border-border rounded-lg px-3 py-2 text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              autoComplete="current-password"
              required
            />
          </div>
          {error && <p className="text-sm text-destructive text-center">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="bg-primary text-primary-foreground rounded-lg py-2 text-sm font-semibold hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? "Connexion…" : "Se connecter"}
          </button>
        </form>
      </div>
    </div>
  )
}
