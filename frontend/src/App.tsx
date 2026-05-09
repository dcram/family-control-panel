import type { ReactNode } from "react"
import { Navigate, Route, Routes } from "react-router-dom"
import { useCurrentParent } from "@/hooks/useCurrentParent"
import { CatalogView } from "@/views/CatalogView"
import { ChildrenView } from "@/views/ChildrenView"
import { KioskView } from "@/views/KioskView"
import { LoginView } from "@/views/LoginView"
import { PlanningView } from "@/views/PlanningView"
import { SettingsView } from "@/views/SettingsView"

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { data: parent, isLoading } = useCurrentParent()
  if (isLoading) return <div className="flex h-screen items-center justify-center text-muted-foreground">Chargement…</div>
  if (!parent) return <Navigate to="/login" replace />
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<KioskView />} />
      <Route path="/login" element={<LoginView />} />
      <Route path="/planning" element={<ProtectedRoute><PlanningView /></ProtectedRoute>} />
      <Route path="/children" element={<ProtectedRoute><ChildrenView /></ProtectedRoute>} />
      <Route path="/catalog" element={<ProtectedRoute><CatalogView /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsView /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
