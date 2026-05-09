import { useCallback, useState } from "react"
import { cn } from "@/lib/utils"
import type { TaskState } from "@/types"
import { ChildBadge } from "./ChildBadge"

type PinPadStep =
  | "pin_entry"
  | "pin_error"
  | "parent_choice"
  | "invalid_reason"
  | "child_already_declared"

type InvalidReason = "refused" | "other"

interface VerifyPinResult {
  holder_type: string
  holder_id: string
}

interface PinPadProps {
  taskLabel: string
  taskEmoji: string | null
  childFirstName: string
  childColor: string
  taskState: TaskState
  onVerifyPin: (pin: string) => Promise<VerifyPinResult | null>
  onDeclare: (holderId: string) => void
  onValidate: () => void
  onInvalidate: (reason: InvalidReason) => void
  onClose: () => void
}

export function PinPad({
  taskLabel,
  taskEmoji,
  childFirstName,
  childColor,
  taskState,
  onVerifyPin,
  onDeclare,
  onValidate,
  onInvalidate,
  onClose,
}: PinPadProps) {
  const [digits, setDigits] = useState<string[]>([])
  const [step, setStep] = useState<PinPadStep>("pin_entry")
  const [shake, setShake] = useState(false)

  const submitPin = useCallback(
    async (pin: string) => {
      const result = await onVerifyPin(pin)
      if (!result) {
        setShake(true)
        setTimeout(() => {
          setShake(false)
          setDigits([])
          setStep("pin_entry")
        }, 600)
        setStep("pin_error")
        return
      }
      if (result.holder_type === "parent") {
        setStep("parent_choice")
      } else {
        if (taskState === "declared") {
          setStep("child_already_declared")
          setTimeout(() => onClose(), 1500)
        } else {
          onDeclare(result.holder_id)
        }
      }
    },
    [onVerifyPin, onDeclare, onClose, taskState],
  )

  function pressDigit(d: string) {
    if (digits.length >= 4 || (step !== "pin_entry" && step !== "pin_error")) return
    const next = [...digits, d]
    setDigits(next)
    if (next.length === 4) {
      void submitPin(next.join(""))
    }
  }

  function backspace() {
    setDigits((prev) => prev.slice(0, -1))
  }

  function clearAll() {
    setDigits([])
    setStep("pin_entry")
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={onClose}
    >
      <div
        className={cn(
          "bg-card rounded-2xl shadow-2xl p-6 w-72 flex flex-col gap-4",
          shake && "animate-shake",
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Résumé tâche */}
        <div className="text-center">
          <div className="text-3xl mb-1">{taskEmoji ?? "✓"}</div>
          <p className="font-semibold text-sm">{taskLabel}</p>
          <ChildBadge firstName={childFirstName} color={childColor} size="md" />
        </div>

        {/* Affichage PIN */}
        {(step === "pin_entry" || step === "pin_error") && (
          <>
            <div className="flex justify-center gap-3">
              {[0, 1, 2, 3].map((i) => (
                <div
                  key={i}
                  className={cn(
                    "w-4 h-4 rounded-full border-2",
                    i < digits.length
                      ? "bg-primary border-primary"
                      : "border-muted-foreground",
                  )}
                />
              ))}
            </div>
            {step === "pin_error" && (
              <p className="text-center text-xs text-destructive">PIN incorrect</p>
            )}
            {/* Pavé numérique */}
            <div className="grid grid-cols-3 gap-2">
              {["1","2","3","4","5","6","7","8","9"].map((d) => (
                <DigitBtn key={d} digit={d} onPress={pressDigit} />
              ))}
              <button
                type="button"
                onClick={clearAll}
                className="h-14 rounded-xl bg-muted text-muted-foreground text-xs font-medium active:scale-95 transition-transform"
              >
                ✕
              </button>
              <DigitBtn digit="0" onPress={pressDigit} />
              <button
                type="button"
                onClick={backspace}
                className="h-14 rounded-xl bg-muted text-muted-foreground text-sm font-medium active:scale-95 transition-transform"
              >
                ⌫
              </button>
            </div>
          </>
        )}

        {/* Choix parent */}
        {step === "parent_choice" && (
          <div className="flex flex-col gap-2">
            <p className="text-center text-sm text-muted-foreground">Parent identifié</p>
            <button
              type="button"
              onClick={() => onValidate()}
              className="w-full py-3 rounded-xl bg-green-100 text-green-700 font-semibold hover:bg-green-200"
            >
              ✓ Valider
            </button>
            <button
              type="button"
              onClick={() => setStep("invalid_reason")}
              className="w-full py-3 rounded-xl bg-red-100 text-red-700 font-semibold hover:bg-red-200"
            >
              ✗ Invalider
            </button>
          </div>
        )}

        {/* Motif invalidation */}
        {step === "invalid_reason" && (
          <div className="flex flex-col gap-2">
            <p className="text-center text-sm text-muted-foreground">Motif</p>
            <button
              type="button"
              onClick={() => onInvalidate("refused")}
              className="w-full py-3 rounded-xl bg-muted font-medium hover:bg-muted/80"
            >
              Refus d'obtempérer
            </button>
            <button
              type="button"
              onClick={() => onInvalidate("other")}
              className="w-full py-3 rounded-xl bg-muted font-medium hover:bg-muted/80"
            >
              Autre raison
            </button>
          </div>
        )}

        {/* Déjà déclarée */}
        {step === "child_already_declared" && (
          <p className="text-center text-sm text-muted-foreground py-2">
            Tâche déjà déclarée — en attente de validation parentale
          </p>
        )}

        <button
          type="button"
          onClick={onClose}
          className="text-xs text-muted-foreground text-center hover:underline"
        >
          Annuler
        </button>
      </div>
    </div>
  )
}

function DigitBtn({ digit, onPress }: { digit: string; onPress: (d: string) => void }) {
  return (
    <button
      type="button"
      onClick={() => onPress(digit)}
      className="h-14 rounded-xl bg-muted text-foreground text-xl font-semibold active:scale-95 transition-transform hover:bg-muted/80"
    >
      {digit}
    </button>
  )
}
