import { Reveal } from "./utils";

const techs = [
  {
    name: "React",
    logo: (
      <svg viewBox="-4 -4 32 32" className="w-6 h-6" fill="none">
        <circle cx="12" cy="12" r="2.5" fill="#FF5722" />
        <ellipse cx="12" cy="12" rx="10" ry="4" stroke="#F1F1F1" strokeWidth="1.5" />
        <ellipse cx="12" cy="12" rx="10" ry="4" stroke="#F1F1F1" strokeWidth="1.5" transform="rotate(60 12 12)" />
        <ellipse cx="12" cy="12" rx="10" ry="4" stroke="#F1F1F1" strokeWidth="1.5" transform="rotate(120 12 12)" />
      </svg>
    ),
  },
  {
    name: "TypeScript",
    logo: (
      <svg viewBox="0 0 32 32" className="w-6 h-6" fill="none">
        <rect x="1" y="1" width="30" height="30" rx="2" stroke="#F1F1F1" strokeWidth="2" />
        <text x="16" y="23" textAnchor="middle" fill="#F1F1F1" fontSize="14" fontWeight="bold" fontFamily="sans-serif">TS</text>
      </svg>
    ),
  },
  {
    name: "Tailwind CSS",
    logo: (
      <svg viewBox="0 0 32 20" className="w-6 h-6" fill="none">
        <path
          d="M16 2c-4 0-6.5 2-7.5 6 1.5-2 3.3-2.75 5.5-2.25 1.2.28 2.05 1.08 3 1.95C18.6 9 20.2 10.5 23 10.5c4 0 6.5-2 7.5-6-1.5 2-3.25 2.75-5.5 2.25-1.18-.28-2.02-1.08-2.97-1.95C20.5 3.5 18.9 2 16 2ZM8 12c-4 0-6.5 2-7.5 6 1.5-2 3.25-2.75 5.5-2.25 1.18.28 2.02 1.08 2.97 1.95C10.5 19.5 12.1 21 15 21c4 0 6.5-2 7.5-6-1.5 2-3.3 2.75-5.5 2.25-1.2-.28-2.05-1.08-3-1.95C12.4 14 10.8 12.5 8 12Z"
          fill="#F1F1F1"
        />
      </svg>
    ),
  },
  {
    name: "Vite",
    logo: (
      <svg viewBox="0 0 32 32" className="w-6 h-6" fill="none">
        <path
          d="m28.5 5.5-12 22.5c-.2.4-.8.4-1 0L3.5 5.5c-.3-.5.2-1 .7-.7l11.5 8.8L27.8 4.8c.5-.3 1 .2.7.7Z"
          stroke="#F1F1F1" strokeWidth="2" strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    name: "Lucide",
    logo: (
      <svg viewBox="0 0 32 32" className="w-6 h-6" fill="none" stroke="#F1F1F1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 5a20.5 20.5 0 0 0-3.5 1.8c-2.2 1.2-4.2 2.5-5.2 4.3-.6 1.2.2 2.5 1.3 3.2A19 19 0 0 0 8 16" />
        <path d="M21 5a20.5 20.5 0 0 1 3.5 1.8c2.2 1.2 4.2 2.5 5.2 4.3.6 1.2-.2 2.5-1.3 3.2A19 19 0 0 1 24 16" />
        <circle cx="16" cy="16" r="1.5" fill="#FF5722" />
        <path d="M5 27a21 21 0 0 0 3.5 1.8c2.2 1.2 4.2.8 5.2-1 .6-1.2-.2-2.5-1.3-3.2A19 19 0 0 0 8 22" />
        <path d="M27 27a21 21 0 0 1-3.5 1.8c-2.2 1.2-4.2.8-5.2-1-.6-1.2.2-2.5 1.3-3.2A19 19 0 0 1 24 22" />
        <path d="M12 9c1.5-1 3-1.5 3.5 0" />
        <path d="M20 9c-1.5-1-3-1.5-3.5 0" />
      </svg>
    ),
  },
  {
    name: "Framer Motion",
    logo: (
      <svg viewBox="0 0 32 32" className="w-6 h-6" fill="none">
        <path d="M6 16h20v10H6z" stroke="#F1F1F1" strokeWidth="2" />
        <path d="M6 6h10v10H6z" fill="#FF5722" />
        <path d="M16 16h10v10H16z" stroke="#F1F1F1" strokeWidth="2" />
      </svg>
    ),
  },
];

const row = [...techs, ...techs];

export default function TechStack() {
  return (
    <section id="tech-stack" className="py-24 overflow-hidden border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-6xl mx-auto px-4">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              Technical Stack
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium max-w-xl mx-auto">
              Built with modern tools that prioritize developer experience and performance.
            </p>
          </div>
        </Reveal>
      </div>

      <div className="relative border-y-2 border-[#F1F1F1]/5 py-8">
        <div
          className="flex gap-12 items-center w-max"
          style={{ animation: "marquee 25s linear infinite" }}
        >
          {row.map((t, i) => (
            <div key={i} className="shrink-0 flex items-center gap-3 select-none">
              {t.logo}
              <span className="text-sm font-bold text-[#F1F1F1] whitespace-nowrap uppercase tracking-wider">{t.name}</span>
            </div>
          ))}
        </div>

        <div className="pointer-events-none absolute inset-y-0 left-0 w-32 bg-linear-to-r from-[#2D2D2D] to-transparent z-10" />
        <div className="pointer-events-none absolute inset-y-0 right-0 w-32 bg-linear-to-r from-transparent to-[#2D2D2D] z-10" />
      </div>

      <style>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
    </section>
  );
}
