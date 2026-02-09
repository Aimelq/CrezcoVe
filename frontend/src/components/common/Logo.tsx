import { cn } from '@/lib/utils'

interface LogoProps {
    className?: string
    showText?: boolean
    size?: 'sm' | 'md' | 'lg' | 'xl'
    variant?: 'light' | 'dark'
}

export default function Logo({
    className,
    showText = true,
    size = 'md',
    variant = 'dark'
}: LogoProps) {
    const sizes = {
        sm: 'h-9',
        md: 'h-12',
        lg: 'h-24',
        xl: 'h-40'
    }

    return (
        <div className={cn("flex items-center gap-3", className)}>
            <div className={cn(sizes[size], "aspect-square relative flex items-center justify-center overflow-visible")}>
                <svg
                    viewBox="-10 -10 120 120"
                    className="w-full h-full overflow-visible drop-shadow-sm"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    {/* Background circular circuit pattern */}
                    <circle cx="50" cy="55" r="38" className="stroke-blue-500/10" strokeWidth="1" />
                    <circle cx="50" cy="55" r="32" className="stroke-blue-500/20" strokeWidth="1.5" />

                    {/* Circuit Lines */}
                    <path d="M30 45C30 35 40 30 50 30" className="stroke-blue-400" strokeWidth="1" strokeDasharray="2 2" />
                    <path d="M70 45C70 35 60 30 50 30" className="stroke-blue-400" strokeWidth="1" strokeDasharray="2 2" />

                    <path d="M25 65L15 75" className="stroke-blue-500" strokeWidth="1.5" strokeLinecap="round" />
                    <circle cx="15" cy="75" r="2" className="fill-blue-500" />

                    <path d="M75 65L85 75" className="stroke-blue-600" strokeWidth="1.5" strokeLinecap="round" />
                    <circle cx="85" cy="75" r="2" className="fill-blue-600" />

                    <path d="M40 85L35 90" className="stroke-blue-300" strokeWidth="1" strokeLinecap="round" />
                    <path d="M60 85L65 90" className="stroke-blue-300" strokeWidth="1" strokeLinecap="round" />

                    {/* Main Arrow with Gradient (defined below) */}
                    <path
                        d="M50 90V30M50 30L35 45M50 30L65 45"
                        stroke="url(#logo-gradient)"
                        strokeWidth="10"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />

                    {/* Digital Pixel Squares */}
                    <rect x="46" y="18" width="8" height="8" className="fill-blue-400" rx="1" />
                    <rect x="56" y="12" width="6" height="6" className="fill-blue-500" rx="1" />
                    <rect x="38" y="12" width="6" height="6" className="fill-blue-300" rx="1" />
                    <rect x="50" y="4" width="5" height="5" className="fill-blue-600" rx="1" />
                    <rect x="42" y="6" width="4" height="4" className="fill-blue-400" rx="1" />

                    {/* Gradient Definition */}
                    <defs>
                        <linearGradient id="logo-gradient" x1="50" y1="90" x2="50" y2="30" gradientUnits="userSpaceOnUse">
                            <stop offset="0" stopColor="#1e3a8a" /> {/* indigo-900 */}
                            <stop offset="0.5" stopColor="#2563eb" /> {/* blue-600 */}
                            <stop offset="1" stopColor="#3b82f6" /> {/* blue-500 */}
                        </linearGradient>
                    </defs>
                </svg>
            </div>

            {showText && (
                <div className="flex flex-col leading-[0.9]">
                    <span className={cn(
                        "font-bold tracking-tight",
                        size === 'sm' ? "text-lg" : "text-2xl",
                        variant === 'dark' ? "text-slate-900" : "text-white"
                    )}>
                        <span className="font-extrabold uppercase">Crezco</span>
                        <span className="text-blue-600">Ve</span>
                    </span>
                    {size !== 'sm' && (
                        <span className={cn(
                            "text-[10px] font-bold uppercase tracking-[0.2em] mt-0.5",
                            variant === 'dark' ? "text-slate-500" : "text-slate-300"
                        )}>
                            Gestión Inteligente
                        </span>
                    )}
                </div>
            )}
        </div>
    )
}
