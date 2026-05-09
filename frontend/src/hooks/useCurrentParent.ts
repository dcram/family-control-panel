import { useQuery } from "@tanstack/react-query"
import type { Parent } from "@/types"

async function fetchMe(): Promise<Parent | null> {
  const res = await fetch("/api/v1/auth/me", { credentials: "include" })
  if (!res.ok) return null
  return res.json() as Promise<Parent>
}

export function useCurrentParent() {
  return useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}
