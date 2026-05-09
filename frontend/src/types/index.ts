// --- Entités ---

export interface Child {
  id: string
  first_name: string
  date_of_birth: string
  color: string
  sort_order: number
  archived_at: string | null
}

export interface Task {
  id: string
  label: string
  emoji: string | null
  min_age: number
  duration_minutes: number
  archived_at: string | null
}

export interface Moment {
  id: string
  label: string
  start_time: string
  end_time: string
  sort_order: number
}

export interface Assignment {
  id: string
  task_id: string
  child_id: string
  moment_id: string
  day_of_week: number
  created_at: string
}

// --- Instances ---

export type TaskState = "assigned" | "declared" | "done" | "undone" | "unknown"

export interface TaskInstance {
  id: string
  assignment_id: string | null
  week_start: string
  instance_date: string
  state: TaskState
  declared_at: string | null
  state_changed_at: string | null
  task_label: string
  task_emoji: string | null
  task_duration_minutes: number
  child_first_name: string
  child_color: string
  moment_label: string
  day_of_week: number
}

// --- Kiosque ---

export interface KioskInfo {
  date: string
  saint: string | null
  weather: string | null
  quote_text: string | null
  quote_author: string | null
  quote_work: string | null
}

export interface KioskConfig {
  weather_city: string
  quote_text: string | null
  quote_author: string | null
  quote_work: string | null
}

// --- Planning ---

export type WeekPlanning = TaskInstance[]

// --- Auth ---

export interface Parent {
  id: string
  login: string
}
