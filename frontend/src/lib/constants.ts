export const CHILD_COLORS = [
  "green",
  "blue",
  "amber",
  "coral",
  "purple",
  "gray",
] as const

export type ChildColor = (typeof CHILD_COLORS)[number]

// Classes Tailwind bg/text par couleur enfant
export const CHILD_COLOR_BG: Record<ChildColor, string> = {
  green: "bg-child-green",
  blue: "bg-child-blue",
  amber: "bg-child-amber",
  coral: "bg-child-coral",
  purple: "bg-child-purple",
  gray: "bg-child-gray",
}

export const CHILD_COLOR_TEXT: Record<ChildColor, string> = {
  green: "text-child-green",
  blue: "text-child-blue",
  amber: "text-child-amber",
  coral: "text-child-coral",
  purple: "text-child-purple",
  gray: "text-child-gray",
}

// Jours de la semaine (0 = lundi)
export const DAY_LABELS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"] as const
