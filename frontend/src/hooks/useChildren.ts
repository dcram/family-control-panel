import { useQuery, useQueryClient } from "@tanstack/react-query"
import type { Child } from "@/types"

async function fetchChildren(): Promise<Child[]> {
  const res = await fetch("/api/v1/children/", { credentials: "include" })
  if (!res.ok) throw new Error("Erreur enfants")
  return res.json() as Promise<Child[]>
}

export function useChildren() {
  return useQuery({ queryKey: ["children"], queryFn: fetchChildren })
}

export function useInvalidateChildren() {
  const qc = useQueryClient()
  return () => qc.invalidateQueries({ queryKey: ["children"] })
}
