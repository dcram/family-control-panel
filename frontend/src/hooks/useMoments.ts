import { useQuery } from "@tanstack/react-query"
import type { Moment } from "@/types"

export function useMoments() {
  return useQuery({
    queryKey: ["moments"],
    queryFn: async () => {
      const res = await fetch("/api/v1/moments/", { credentials: "include" })
      if (!res.ok) throw new Error("Erreur moments")
      return res.json() as Promise<Moment[]>
    },
    staleTime: Infinity,
  })
}
