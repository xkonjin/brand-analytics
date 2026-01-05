// =============================================================================
// Glass Input Component
// =============================================================================
// Modern glass-styled input with proper focus states for dark theme.
// =============================================================================

import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Input size variant */
  inputSize?: "sm" | "default" | "lg";
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, inputSize = "default", ...props }, ref) => {
    const sizeClasses = {
      sm: "h-9 px-3 text-sm rounded-lg",
      default: "h-11 px-4 text-sm rounded-xl",
      lg: "h-12 px-4 text-base rounded-xl",
    };

    return (
      <input
        type={type}
        className={cn(
          // Base styles
          "flex w-full transition-all duration-150",
          // Glass styling
          "bg-white/[0.04] backdrop-blur-md",
          "border border-white/[0.1]",
          "text-white placeholder:text-white/40",
          // Focus states - prominent ring for accessibility
          "focus:outline-none focus:bg-white/[0.06]",
          "focus:border-white/[0.2] focus:ring-2 focus:ring-blue-500/40",
          // File input
          "file:border-0 file:bg-white/[0.1] file:text-white file:text-sm file:font-medium",
          "file:mr-4 file:py-2 file:px-4 file:rounded-lg",
          // Disabled state
          "disabled:cursor-not-allowed disabled:opacity-50",
          // Size
          sizeClasses[inputSize],
          className,
        )}
        ref={ref}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";

// =============================================================================
// Glass Textarea Component
// =============================================================================

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          // Base styles
          "flex w-full min-h-[100px] transition-all duration-150 resize-none",
          // Glass styling
          "bg-white/[0.04] backdrop-blur-md rounded-xl",
          "border border-white/[0.1]",
          "px-4 py-3 text-sm text-white placeholder:text-white/40",
          // Focus states
          "focus:outline-none focus:bg-white/[0.06]",
          "focus:border-white/[0.2] focus:ring-2 focus:ring-blue-500/40",
          // Disabled state
          "disabled:cursor-not-allowed disabled:opacity-50",
          className,
        )}
        ref={ref}
        {...props}
      />
    );
  },
);
Textarea.displayName = "Textarea";

export { Input, Textarea };
