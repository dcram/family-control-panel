import { useQuery, useQueryClient } from "@tanstack/react-query"
import type { Task } from "@/types"

async function fetchTasks(): Promise<Task[]> {
  const res = await fetch("/api/v1/tasks/", { credentials: "include" })
  if (!res.ok) throw new Error("Erreur tâches")
  return res.json() as Promise<Task[]>
}

export function useTasks() {
  return useQuery({ queryKey: ["tasks"], queryFn: fetchTasks })
}

export function useInvalidateTasks() {
  const qc = useQueryClient()
  return () => qc.invalidateQueries({ queryKey: ["tasks"] })
}
