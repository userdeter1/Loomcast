// A small woven "loom" mark: interlaced threads.
export default function Logo({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="url(#loom-g)" />
      <g stroke="white" strokeWidth="2" strokeLinecap="round" opacity="0.95">
        <path d="M8 10h16" />
        <path d="M8 16h16" />
        <path d="M8 22h16" />
        <path d="M11 7v18" opacity="0.55" />
        <path d="M16 7v18" opacity="0.55" />
        <path d="M21 7v18" opacity="0.55" />
      </g>
      <defs>
        <linearGradient id="loom-g" x1="0" y1="0" x2="32" y2="32">
          <stop stopColor="#6d63f2" />
          <stop offset="1" stopColor="#4f39c5" />
        </linearGradient>
      </defs>
    </svg>
  );
}
