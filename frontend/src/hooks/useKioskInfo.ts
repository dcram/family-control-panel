import { useQuery } from "@tanstack/react-query"
import type { KioskInfo } from "@/types"

async function fetchKioskInfo(): Promise<KioskInfo> {
  const res = await fetch("/api/v1/kiosk/info")
  if (!res.ok) throw new Error(`Erreur ${res.status}`)
  return res.json() as Promise<KioskInfo>
}

export function useKioskInfo() {
  return useQuery({
    queryKey: ["kiosk-info"],
    queryFn: fetchKioskInfo,
    // Rafraîchissement toutes les 15 min (bascule 30h lazy côté serveur)
    refetchInterval: 15 * 60 * 1000,
    staleTime: 5 * 60 * 1000,
  })
}
