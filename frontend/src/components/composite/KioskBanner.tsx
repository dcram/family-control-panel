import { DAY_LABELS } from "@/lib/constants"

interface KioskBannerProps {
  date: Date
  saint: string | null
  weather: string | null
  quoteText: string | null
  quoteAuthor: string | null
}

const MONTH_LABELS = [
  "jan.", "fév.", "mar.", "avr.", "mai", "juin",
  "juil.", "aoû.", "sep.", "oct.", "nov.", "déc.",
]

export function KioskBanner({ date, saint, weather, quoteText, quoteAuthor }: KioskBannerProps) {
  const dayLabel = DAY_LABELS[date.getDay() === 0 ? 6 : date.getDay() - 1]
  const dayNum = date.getDate()
  const monthLabel = MONTH_LABELS[date.getMonth()]
  const truncatedQuote = quoteText && quoteText.length > 120
    ? quoteText.slice(0, 120) + "…"
    : quoteText

  return (
    <div className="sticky top-0 z-10 bg-background border-b border-border px-4 py-2 flex items-center justify-between gap-4">
      {/* Gauche : saint + date */}
      <div className="flex flex-col min-w-0">
        {saint && (
          <span className="text-xs text-muted-foreground truncate">Ste/St {saint}</span>
        )}
        <span className="text-sm font-semibold capitalize">
          {dayLabel.toLowerCase()} {dayNum} {monthLabel}
        </span>
      </div>

      {/* Centre : citation */}
      {truncatedQuote && (
        <div className="flex-1 text-center min-w-0 px-4">
          <p className="text-xs text-muted-foreground italic truncate">« {truncatedQuote} »</p>
          {quoteAuthor && (
            <p className="text-[10px] text-muted-foreground/70">— {quoteAuthor}</p>
          )}
        </div>
      )}

      {/* Droite : météo + slot bus (réservé) */}
      <div className="flex flex-col items-end min-w-0">
        {weather && (
          <span className="text-sm font-medium whitespace-nowrap">{weather}</span>
        )}
        {/* Slot horaires bus — Cycle 2 */}
      </div>
    </div>
  )
}
