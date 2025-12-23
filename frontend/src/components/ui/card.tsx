// =============================================================================
// Glass Card Components - Apple Liquid Glass UI
// =============================================================================
// Translucent card components with backdrop blur, glow effects, and depth.
// =============================================================================

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

// Card variants for different glass intensities and effects
const cardVariants = cva(
  "rounded-2xl border transition-all duration-300 ease-out overflow-hidden",
  {
    variants: {
      variant: {
        // Default glass card
        default: [
          "bg-white/[0.06] backdrop-blur-xl border-white/[0.1]",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25)]",
        ],
        // Light glass - more transparent
        light: [
          "bg-white/[0.04] backdrop-blur-md border-white/[0.08]",
          "shadow-[0_4px_16px_rgba(0,0,0,0.2)]",
        ],
        // Heavy glass - more opaque
        heavy: [
          "bg-white/[0.12] backdrop-blur-2xl border-white/[0.2]",
          "shadow-[0_16px_48px_rgba(0,0,0,0.35)]",
        ],
        // Interactive glass - with hover effects
        interactive: [
          "bg-white/[0.06] backdrop-blur-xl border-white/[0.1]",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25)]",
          "hover:bg-white/[0.1] hover:border-white/[0.2]",
          "hover:shadow-[0_16px_48px_rgba(0,0,0,0.35)]",
          "hover:-translate-y-1 cursor-pointer",
        ],
        // Glow effect - with colored border glow
        glow: [
          "bg-white/[0.06] backdrop-blur-xl border-white/[0.15]",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_30px_rgba(59,130,246,0.1)]",
          "hover:shadow-[0_16px_48px_rgba(0,0,0,0.35),0_0_40px_rgba(59,130,246,0.2)]",
          "hover:-translate-y-1",
        ],
        // Score cards with semantic colors
        excellent: [
          "bg-white/[0.06] backdrop-blur-xl border-emerald-500/30",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_20px_rgba(16,185,129,0.15)]",
        ],
        good: [
          "bg-white/[0.06] backdrop-blur-xl border-green-500/30",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_20px_rgba(34,197,94,0.15)]",
        ],
        average: [
          "bg-white/[0.06] backdrop-blur-xl border-yellow-500/30",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_20px_rgba(234,179,8,0.15)]",
        ],
        poor: [
          "bg-white/[0.06] backdrop-blur-xl border-orange-500/30",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_20px_rgba(249,115,22,0.15)]",
        ],
        critical: [
          "bg-white/[0.06] backdrop-blur-xl border-red-500/30",
          "shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_20px_rgba(239,68,68,0.15)]",
        ],
      },
      size: {
        default: "p-6",
        sm: "p-4",
        lg: "p-8",
        none: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, size, className }))}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-xl font-semibold leading-none tracking-tight text-white",
      "drop-shadow-[0_2px_4px_rgba(0,0,0,0.3)]",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-white/60", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

// =============================================================================
// Glass-Specific Card Variants
// =============================================================================

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  intensity?: 'light' | 'medium' | 'heavy'
  glow?: boolean
  interactive?: boolean
}

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, intensity = 'medium', glow = false, interactive = false, ...props }, ref) => {
    const intensityClasses = {
      light: 'bg-white/[0.04] backdrop-blur-md border-white/[0.08]',
      medium: 'bg-white/[0.08] backdrop-blur-xl border-white/[0.12]',
      heavy: 'bg-white/[0.12] backdrop-blur-2xl border-white/[0.2]',
    }

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl border transition-all duration-300 ease-out',
          intensityClasses[intensity],
          'shadow-[0_8px_32px_rgba(0,0,0,0.25)]',
          glow && 'shadow-[0_8px_32px_rgba(0,0,0,0.25),0_0_30px_rgba(59,130,246,0.15)]',
          interactive && [
            'cursor-pointer',
            'hover:bg-white/[0.12] hover:border-white/[0.2]',
            'hover:shadow-[0_16px_48px_rgba(0,0,0,0.35)]',
            'hover:-translate-y-1',
            'active:scale-[0.98]',
          ],
          className
        )}
        {...props}
      />
    )
  }
)
GlassCard.displayName = "GlassCard"

// Score-based card that automatically applies the right glow color
interface ScoreCardProps extends React.HTMLAttributes<HTMLDivElement> {
  score: number
  interactive?: boolean
}

const ScoreCard = React.forwardRef<HTMLDivElement, ScoreCardProps>(
  ({ className, score, interactive = false, ...props }, ref) => {
    const getScoreVariant = (score: number) => {
      if (score >= 80) return 'excellent'
      if (score >= 70) return 'good'
      if (score >= 60) return 'average'
      if (score >= 50) return 'poor'
      return 'critical'
    }

    const variant = getScoreVariant(score)

    return (
      <Card
        ref={ref}
        variant={variant as any}
        className={cn(
          interactive && [
            'cursor-pointer',
            'hover:-translate-y-1',
            'active:scale-[0.98]',
          ],
          className
        )}
        {...props}
      />
    )
  }
)
ScoreCard.displayName = "ScoreCard"

export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent,
  GlassCard,
  ScoreCard,
  cardVariants,
}
