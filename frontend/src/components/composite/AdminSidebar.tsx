import {
  IconCalendar,
  IconList,
  IconLogout,
  IconSettings,
  IconUsers,
} from "@tabler/icons-react"
import { cn } from "@/lib/utils"

export type AdminSection = "planning" | "children" | "catalog" | "settings"

interface AdminSidebarProps {
  activeSection: AdminSection
  onNavigate: (section: AdminSection) => void
  onLogout: () => void
}

interface NavItem {
  section: AdminSection
  label: string
  icon: React.ReactNode
}

const NAV_ITEMS: NavItem[] = [
  { section: "planning", label: "Planning", icon: <IconCalendar size={18} /> },
  { section: "children", label: "Enfants", icon: <IconUsers size={18} /> },
  { section: "catalog", label: "Catalogue", icon: <IconList size={18} /> },
  { section: "settings", label: "Paramètres", icon: <IconSettings size={18} /> },
]

export function AdminSidebar({ activeSection, onNavigate, onLogout }: AdminSidebarProps) {
  return (
    <nav className="flex flex-col w-36 h-full bg-background border-r border-border py-4 px-2 flex-shrink-0">
      <div className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map(({ section, label, icon }) => (
          <button
            key={section}
            type="button"
            onClick={() => onNavigate(section)}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors text-left",
              activeSection === section
                ? "bg-primary text-primary-foreground font-semibold"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground",
            )}
          >
            {icon}
            {label}
          </button>
        ))}
      </div>
      <div className="mt-auto border-t border-border pt-2">
        <button
          type="button"
          onClick={onLogout}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors w-full"
        >
          <IconLogout size={18} />
          Déconnexion
        </button>
      </div>
    </nav>
  )
}
