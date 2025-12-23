// =============================================================================
// Glass Button Components - Apple Liquid Glass UI
// =============================================================================
// Beautiful glass buttons with hover effects, glow, and spring animations.
// =============================================================================

import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2 whitespace-nowrap",
    "rounded-xl font-medium transition-all duration-200 ease-out",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent",
    "disabled:pointer-events-none disabled:opacity-50",
    "select-none touch-manipulation",
  ],
  {
    variants: {
      variant: {
        // Primary glass button with gradient
        default: [
          "bg-gradient-to-br from-blue-500 to-purple-600 text-white",
          "border border-white/20 backdrop-blur-md",
          "shadow-[0_8px_32px_rgba(59,130,246,0.3)]",
          "hover:shadow-[0_12px_40px_rgba(59,130,246,0.4)]",
          "hover:scale-[1.02] hover:brightness-110",
          "active:scale-[0.98]",
        ],
        // Glass button - translucent
        glass: [
          "bg-white/[0.1] backdrop-blur-md text-white",
          "border border-white/20",
          "shadow-[0_4px_16px_rgba(0,0,0,0.2)]",
          "hover:bg-white/[0.15] hover:border-white/30",
          "hover:shadow-[0_8px_32px_rgba(0,0,0,0.3)]",
          "hover:scale-[1.02]",
          "active:scale-[0.98] active:bg-white/[0.2]",
        ],
        // Secondary - subtle glass
        secondary: [
          "bg-white/[0.06] backdrop-blur-sm text-white/90",
          "border border-white/10",
          "hover:bg-white/[0.1] hover:text-white hover:border-white/20",
          "active:bg-white/[0.15]",
        ],
        // Ghost - minimal
        ghost: [
          "bg-transparent text-white/80",
          "hover:bg-white/[0.08] hover:text-white",
          "active:bg-white/[0.12]",
        ],
        // Outline - border only
        outline: [
          "bg-transparent text-white",
          "border border-white/30",
          "hover:bg-white/[0.08] hover:border-white/50",
          "active:bg-white/[0.12]",
        ],
        // Destructive - for dangerous actions
        destructive: [
          "bg-gradient-to-br from-red-500 to-red-600 text-white",
          "border border-red-400/20 backdrop-blur-md",
          "shadow-[0_8px_32px_rgba(239,68,68,0.3)]",
          "hover:shadow-[0_12px_40px_rgba(239,68,68,0.4)]",
          "hover:scale-[1.02] hover:brightness-110",
          "active:scale-[0.98]",
        ],
        // Success - for positive actions
        success: [
          "bg-gradient-to-br from-emerald-500 to-emerald-600 text-white",
          "border border-emerald-400/20 backdrop-blur-md",
          "shadow-[0_8px_32px_rgba(16,185,129,0.3)]",
          "hover:shadow-[0_12px_40px_rgba(16,185,129,0.4)]",
          "hover:scale-[1.02] hover:brightness-110",
          "active:scale-[0.98]",
        ],
        // Glow - with animated glow effect
        glow: [
          "bg-gradient-to-br from-blue-500 to-purple-600 text-white",
          "border border-white/20 backdrop-blur-md",
          "shadow-[0_0_30px_rgba(59,130,246,0.4)]",
          "hover:shadow-[0_0_45px_rgba(59,130,246,0.6)]",
          "hover:scale-[1.02]",
          "active:scale-[0.98]",
          "animate-glow-pulse",
        ],
        // Link style
        link: [
          "text-blue-400 underline-offset-4",
          "hover:underline hover:text-blue-300",
        ],
      },
      size: {
        default: "h-11 px-6 py-2.5 text-sm",
        sm: "h-9 px-4 py-2 text-xs rounded-lg",
        lg: "h-12 px-8 py-3 text-base",
        xl: "h-14 px-10 py-4 text-lg",
        icon: "h-10 w-10 p-0",
        "icon-sm": "h-8 w-8 p-0 rounded-lg",
        "icon-lg": "h-12 w-12 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading...</span>
          </>
        ) : (
          children
        )}
      </Comp>
    )
  }
)
Button.displayName = "Button"

// =============================================================================
// Glass-Specific Button Variants
// =============================================================================

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  glow?: boolean
  loading?: boolean
}

const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ className, variant = 'default', size = 'md', glow = false, loading = false, children, disabled, ...props }, ref) => {
    const variantClasses = {
      default: 'bg-white/[0.1] border-white/20 hover:bg-white/[0.15]',
      primary: 'bg-gradient-to-br from-blue-500 to-purple-600 border-white/20',
      secondary: 'bg-white/[0.06] border-white/10 hover:bg-white/[0.1]',
      ghost: 'bg-transparent border-transparent hover:bg-white/[0.08]',
    }

    const sizeClasses = {
      sm: 'h-9 px-4 text-sm rounded-lg',
      md: 'h-11 px-6 text-sm rounded-xl',
      lg: 'h-13 px-8 text-base rounded-xl',
    }

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          'inline-flex items-center justify-center gap-2',
          'font-medium text-white backdrop-blur-md border',
          'transition-all duration-200 ease-out',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50',
          'disabled:opacity-50 disabled:pointer-events-none',
          'hover:scale-[1.02] active:scale-[0.98]',
          variantClasses[variant],
          sizeClasses[size],
          glow && 'shadow-[0_0_30px_rgba(59,130,246,0.3)] hover:shadow-[0_0_40px_rgba(59,130,246,0.4)]',
          className
        )}
        {...props}
      >
        {loading ? (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : null}
        {children}
      </button>
    )
  }
)
GlassButton.displayName = "GlassButton"

// Icon button variant
interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'ghost'
}

const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, size = 'md', variant = 'default', ...props }, ref) => {
    const sizeClasses = {
      sm: 'h-8 w-8',
      md: 'h-10 w-10',
      lg: 'h-12 w-12',
    }

    const variantClasses = {
      default: 'bg-white/[0.1] border border-white/20 hover:bg-white/[0.15]',
      ghost: 'hover:bg-white/[0.1]',
    }

    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-xl',
          'text-white backdrop-blur-sm',
          'transition-all duration-200 ease-out',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50',
          'disabled:opacity-50 disabled:pointer-events-none',
          'hover:scale-105 active:scale-95',
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        {...props}
      />
    )
  }
)
IconButton.displayName = "IconButton"

export { Button, GlassButton, IconButton, buttonVariants }
