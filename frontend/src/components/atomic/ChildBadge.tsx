interface ChildBadgeProps {
  firstName: string
  color: string
  size?: "sm" | "md"
}

const COLOR_HEX: Record<string, string> = {
  green: "#14b8a6",
  blue: "#3b82f6",
  amber: "#f59e0b",
  coral: "#f97316",
  purple: "#8b5cf6",
  gray: "#9ca3af",
}

export function ChildBadge({ firstName, color, size = "sm" }: ChildBadgeProps) {
  const dotSize = size === "sm" ? 7 : 10
  const fontSize = size === "sm" ? 9 : 12

  return (
    <span className="inline-flex items-center gap-1">
      <span
        className="inline-block rounded-full flex-shrink-0"
        style={{
          width: dotSize,
          height: dotSize,
          backgroundColor: COLOR_HEX[color] ?? "#9ca3af",
        }}
      />
      <span style={{ fontSize }} className="text-muted-foreground leading-none">
        {firstName}
      </span>
    </span>
  )
}
