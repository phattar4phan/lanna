import { motion } from "framer-motion";
import ParticleField from "./ParticleField";
import { scrollTo } from "./utils";

const stagger = (i: number) => ({ duration: 0.8, delay: 0.2 + i * 0.1 });

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <ParticleField />

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-20 text-center">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={stagger(0)}
            className="mb-6"
          >
            <span className="inline-block px-4 py-1.5 rounded-full text-sm font-medium tracking-wide border border-brand/20 bg-brand/5 text-brand">
              Experimental AI Research Project
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={stagger(1)}
            className="text-7xl sm:text-8xl md:text-9xl font-black tracking-tight text-brand mb-6"
          >
            LLM
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={stagger(2)}
            className="text-xl sm:text-2xl text-neutral font-light leading-relaxed mb-8 max-w-2xl mx-auto"
          >
            A 50 million parameter language model built for experimentation, curiosity, and learning.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={stagger(3)}
            className="text-base text-neutral/80 leading-relaxed max-w-xl mx-auto mb-12"
          >
            Exploring transformer architectures, tokenization, optimization, training, and inference
            from first principles — not competing with production-scale models, but understanding how
            they work.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={stagger(4)}
            className="flex items-center justify-center"
          >
            <button
              onClick={() => scrollTo("chat")}
              className="group relative px-8 py-3.5 rounded-2xl bg-brand text-[#F9C25B] font-semibold text-base shadow-lg shadow-brand/10 hover:shadow-xl hover:shadow-brand/20 transition-all duration-300 hover:-translate-y-0.5 cursor-pointer"
            >
              Try Chat
              <span className="absolute inset-0 rounded-2xl bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </button>
          </motion.div>
        </motion.div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#F9C25B] to-transparent pointer-events-none z-10" />
    </section>
  );
}
