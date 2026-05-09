import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { AdminSidebar } from "@/components/composite/AdminSidebar"
import type { KioskConfig } from "@/types"

export function SettingsView() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [config, setConfig] = useState<KioskConfig | null>(null)
  const [weatherCity, setWeatherCity] = useState("")
  const [quote, setQuote] = useState({ text: "", author: "", work: "" })
  const [saved, setSaved] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/config/", { credentials: "include" })
      .then((r) => r.json() as Promise<KioskConfig>)
      .then((c) => {
        setConfig(c)
        setWeatherCity(c.weather_city)
        setQuote({
          text: c.quote_text ?? "",
          author: c.quote_author ?? "",
          work: c.quote_work ?? "",
        })
      })
      .catch(() => null)
  }, [])

  async function logout() {
    await fetch("/api/v1/auth/logout", { method: "POST", credentials: "include" })
    await qc.invalidateQueries({ queryKey: ["me"] })
    navigate("/login")
  }

  async function saveWeather(e: React.FormEvent) {
    e.preventDefault()
    await fetch("/api/v1/config/weather", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ weather_city: weatherCity }),
    })
    setSaved("Ville météo enregistrée")
    setTimeout(() => setSaved(null), 2000)
  }

  async function saveQuote(e: React.FormEvent) {
    e.preventDefault()
    await fetch("/api/v1/config/quote", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        quote_text: quote.text || null,
        quote_author: quote.author || null,
        quote_work: quote.work || null,
      }),
    })
    setSaved("Citation enregistrée")
    setTimeout(() => setSaved(null), 2000)
  }

  if (!config) return <div className="flex h-screen"><div className="m-auto text-muted-foreground">Chargement…</div></div>

  return (
    <div className="flex h-screen overflow-hidden">
      <AdminSidebar
        activeSection="settings"
        onNavigate={(s) => navigate(`/${s}`)}
        onLogout={() => void logout()}
      />
      <div className="flex-1 overflow-auto p-6 max-w-lg">
        <h1 className="text-xl font-bold mb-6">Paramètres kiosque</h1>

        {saved && (
          <div className="mb-4 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
            {saved}
          </div>
        )}

        <section className="bg-card border border-border rounded-xl p-4 mb-4">
          <h2 className="font-semibold text-sm mb-3">Météo</h2>
          <form onSubmit={(e) => void saveWeather(e)} className="flex gap-2">
            <input
              className="flex-1 border border-border rounded-lg px-3 py-2 text-sm"
              placeholder="Paris"
              value={weatherCity}
              onChange={(e) => setWeatherCity(e.target.value)}
            />
            <button type="submit" className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm">
              Enregistrer
            </button>
          </form>
        </section>

        <section className="bg-card border border-border rounded-xl p-4">
          <h2 className="font-semibold text-sm mb-3">Citation du moment</h2>
          <form onSubmit={(e) => void saveQuote(e)} className="flex flex-col gap-3">
            <textarea
              className="border border-border rounded-lg px-3 py-2 text-sm resize-none"
              rows={3}
              placeholder="Texte de la citation"
              value={quote.text}
              onChange={(e) => setQuote((q) => ({ ...q, text: e.target.value }))}
            />
            <input
              className="border border-border rounded-lg px-3 py-2 text-sm"
              placeholder="Auteur"
              value={quote.author}
              onChange={(e) => setQuote((q) => ({ ...q, author: e.target.value }))}
            />
            <input
              className="border border-border rounded-lg px-3 py-2 text-sm"
              placeholder="Œuvre (optionnel)"
              value={quote.work}
              onChange={(e) => setQuote((q) => ({ ...q, work: e.target.value }))}
            />
            <button type="submit" className="py-2 rounded-lg bg-primary text-primary-foreground text-sm">
              Enregistrer
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}
