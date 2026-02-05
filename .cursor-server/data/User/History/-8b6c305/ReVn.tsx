import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-[oklch(0.65_0.22_264)] focus-visible:ring-offset-2 focus-visible:ring-offset-[oklch(0.12_0_0)] aria-invalid:ring-[oklch(0.65_0.22_25)]/20",
  {
    variants: {
      variant: {
        default: "bg-[oklch(0.65_0.22_264)] text-white hover:bg-[oklch(0.70_0.22_264)] active:bg-[oklch(0.60_0.22_264)] shadow-sm hover:shadow-md",
        destructive:
          "bg-[oklch(0.65_0.22_25)] text-white hover:bg-[oklch(0.70_0.22_25)] active:bg-[oklch(0.60_0.22_25)] shadow-sm hover:shadow-md focus-visible:ring-[oklch(0.65_0.22_25)]",
        outline:
          "border border-[oklch(1_0_0_/_0.20)] bg-[oklch(0.12_0_0)] text-[oklch(0.90_0_0)] shadow-xs hover:bg-[oklch(0.18_0_0)] hover:text-white hover:border-[oklch(0.65_0.22_264)]",
        secondary:
          "bg-[oklch(0.27_0_0)] text-white hover:bg-[oklch(0.32_0_0)] active:bg-[oklch(0.22_0_0)]",
        ghost:
          "text-[oklch(0.70_0_0)] hover:bg-[oklch(0.18_0_0)] hover:text-white",
        link: "text-[oklch(0.65_0.22_264)] underline-offset-4 hover:underline hover:text-[oklch(0.70_0.22_264)]",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
