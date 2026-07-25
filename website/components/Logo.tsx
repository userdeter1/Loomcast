export default function Logo({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 500 500" fill="none" className={className} aria-hidden="true">
      <defs>
        <linearGradient id="loomcast-logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#8b5cf6"/>
          <stop offset="50%" stopColor="#6366f1"/>
          <stop offset="100%" stopColor="#38bdf8"/>
        </linearGradient>
      </defs>

      {/* Main C-shaped ring arc */}
      <path
        d="M 330 170 A 145 145 0 1 0 330 330"
        fill="none"
        stroke="url(#loomcast-logo-grad)"
        strokeWidth="46"
        strokeLinecap="round"
      />

      {/* Three center ellipsis dots shifted further left */}
      <circle cx="160" cy="250" r="16" fill="#8b5cf6"/>
      <circle cx="200" cy="250" r="16" fill="#6366f1"/>
      <circle cx="240" cy="250" r="16" fill="#38bdf8"/>

      {/* Pixel squares shifted left */}
      <rect x="370" y="178" width="18" height="18" rx="4" fill="#38bdf8"/>
      <rect x="318" y="235" width="24" height="24" rx="5" fill="#38bdf8"/>
      <rect x="345" y="210" width="24" height="24" rx="5" fill="#38bdf8"/>
      <rect x="375" y="218" width="38" height="38" rx="8" fill="#38bdf8"/>
      <rect x="352" y="262" width="18" height="18" rx="4" fill="#38bdf8"/>
    </svg>
  );
}
