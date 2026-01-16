import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// --- Glowing Button ---
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost';
}
export const PremiumButton = ({ className, variant = 'primary', ...props }: ButtonProps) => {
    const base = "px-6 py-3 rounded-lg font-bold tracking-wide transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed";
    const variants = {
        primary: "bg-gradient-to-r from-gold/80 to-gold text-midnight hover:shadow-[0_0_20px_rgba(251,191,36,0.4)] hover:scale-105",
        secondary: "bg-white/10 border border-white/20 text-white hover:bg-white/20 hover:border-gold/50",
        ghost: "bg-transparent text-gold hover:text-white"
    };

    return (
        <button className={cn(base, variants[variant], className)} {...props} />
    );
};

// --- Glass Card ---
export const PremiumCard = ({ className, children }: { className?: string; children: React.ReactNode }) => (
    <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn(
            "bg-midnight/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl relative overflow-hidden",
            "before:absolute before:inset-0 before:bg-gradient-to-br before:from-white/5 before:to-transparent before:pointer-events-none",
            className
        )}
    >
        {children}
    </motion.div>
);

// --- Typewriter Text ---
export const PremiumText = ({ text, className }: { text: any; className?: string }) => {
    // Safety check: handle non-string inputs (objects, arrays) to prevent crashes
    let safeText = "";
    if (typeof text === 'string') {
        safeText = text;
    } else if (text && typeof text === 'object') {
        // If it's the Myth Panel object or similar, try to find a narrative field or just stringify
        safeText = text.narrative || text.description || text.title || JSON.stringify(text);
    } else {
        safeText = String(text || "");
    }

    const words = safeText.split(" ");
    return (
        <p className={cn("leading-relaxed", className)}>
            {words.map((word, i) => (
                <motion.span
                    key={i}
                    initial={{ opacity: 0, filter: 'blur(5px)' }}
                    animate={{ opacity: 1, filter: 'blur(0px)' }}
                    transition={{ delay: i * 0.02, duration: 0.2 }}
                    className="inline-block mr-1"
                >
                    {word}
                </motion.span>
            ))}
        </p>
    );
};

// --- Input Field ---
export const PremiumInput = (props: React.InputHTMLAttributes<HTMLInputElement>) => (
    <div className="relative group">
        <input
            {...props}
            className={cn(
                "w-full bg-black/20 border border-white/10 rounded-xl px-4 py-4 text-white placeholder-white/30",
                "focus:outline-none focus:border-gold/50 focus:bg-black/40 transition-all",
                props.className
            )}
        />
        <div className="absolute inset-0 rounded-xl bg-gold/5 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity" />
    </div>
);
