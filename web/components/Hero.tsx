import { motion } from "framer-motion";
import { scrollTo } from "./utils";

export default function Hero() {
  return (
    <section
      className="relative min-h-screen flex items-center justify-center"
      style={{
        backgroundImage: "radial-gradient(circle, rgba(241,241,241,0.04) 1px, transparent 1px)",
        backgroundSize: "28px 28px",
      }}
    >
      <div className="relative z-10 max-w-3xl mx-auto px-6 py-20 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="mb-8"
          >
            <span className="inline-block px-4 py-1.5 border-2 border-[#F1F1F1]/15 text-sm font-bold tracking-[0.25em] uppercase text-[#F1F1F1]/50">
              Experimental AI Research
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="text-7xl sm:text-8xl md:text-9xl font-black tracking-tight text-[#F1F1F1] mb-6"
          >
            LLM
          </motion.h1>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.5, delay: 0.35 }}
            className="w-20 h-1.5 bg-[#FF5722] mx-auto mb-8 origin-center"
          />

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="text-xl sm:text-2xl text-[#F1F1F1]/75 font-semibold leading-relaxed mb-5 max-w-2xl mx-auto"
          >
            A 50 million parameter language model built for experimentation, curiosity, and learning.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
            className="text-base text-[#F1F1F1]/45 font-medium leading-relaxed max-w-xl mx-auto mb-12"
          >
            Exploring transformer architectures, tokenization, optimization, training, and inference
            from first principles.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.5 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <button
              onClick={() => scrollTo("chat")}
              className="px-8 py-3.5 rounded border-2 border-[#FF5722] bg-[#FF5722] text-[#2D2D2D] font-bold text-base shadow-[4px_4px_0px_#FFC107] hover:shadow-[2px_2px_0px_#FFC107] hover:translate-x-0.5 hover:translate-y-0.5 transition-all duration-100 cursor-pointer"
            >
              Try Chat
            </button>
            <button
              onClick={() => scrollTo("architecture")}
              className="px-8 py-3.5 rounded border-2 border-[#F1F1F1]/15 text-[#F1F1F1] font-bold text-base hover:border-[#FF5722] hover:text-[#FF5722] transition-colors duration-150 cursor-pointer"
            >
              Explore Architecture
            </button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
