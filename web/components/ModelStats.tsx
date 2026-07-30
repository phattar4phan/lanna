import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Reveal } from "./utils";

function useCountUp(target: number, running: boolean) {
  const [count, setCount] = useState(0);
  const frame = useRef<number>(0);

  useEffect(() => {
    if (!running) return;

    const start = performance.now();
    const duration = 2000;

    function tick(now: number) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setCount(Math.floor(eased * target));
      if (p < 1) frame.current = requestAnimationFrame(tick);
      else setCount(target);
    }

    frame.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame.current);
  }, [running, target]);

  return count;
}

function Stat({ value, label, suffix = "" }: { value: number; label: string; suffix?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const count = useCountUp(value, visible);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVisible(true); },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
      className="text-center p-6 border-2 border-[#F1F1F1]/5 hover:border-[#FF5722]/20 transition-colors duration-200"
    >
      <div className="text-3xl sm:text-4xl font-black text-[#FF5722] mb-2 tabular-nums">
        {count.toLocaleString()}
        {suffix}
      </div>
      <div className="text-sm font-bold text-[#F1F1F1]/50 uppercase tracking-wider">{label}</div>
    </motion.div>
  );
}

const stats = [
  { value: 50, label: "Parameters", suffix: "M" },
  { value: 512, label: "Context Length" },
  { value: 32000, label: "Vocabulary Size" },
  { value: 8, label: "Layers" },
  { value: 8, label: "Attention Heads" },
];

export default function ModelStats() {
  return (
    <section id="stats" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-4xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              Model Statistics
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium max-w-xl mx-auto">
              Key numbers that define the current architecture.
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
          {stats.map((s) => (
            <Stat key={s.label} value={s.value} label={s.label} suffix={s.suffix ?? ""} />
          ))}
        </div>
      </div>
    </section>
  );
}
