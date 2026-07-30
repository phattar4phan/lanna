import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { Reveal } from "./utils";

const items = [
  {
    q: "Why only 50 million parameters?",
    a: "50 million is a deliberate choice. It is large enough to demonstrate meaningful language understanding and the core mechanics of transformer architectures, yet small enough to train on modest consumer hardware. This size allows rapid experimentation — you can iterate on ideas, test hypotheses, and learn from failures in hours instead of weeks.",
  },
  {
    q: "Is LLM production-ready?",
    a: "No. LLM is a research and learning project, not a production system. It is not optimized for deployment, throughput, or reliability in production environments. It exists to explore ideas and help understand how language models work. The code is educational and experimental by design.",
  },
  {
    q: "Can others contribute?",
    a: "Absolutely. The project is open source and welcomes contributions from anyone interested in language models — whether you want to experiment with architectures, improve training efficiency, add new features, or simply learn by reading the code. The goal is collaborative learning.",
  },
  {
    q: "Which tokenizer does LLM use?",
    a: "LLM uses SentencePiece with Byte-Pair Encoding. The tokenizer is trained from scratch on the project's curated dataset, with a vocabulary size of approximately 32,000 tokens. This approach provides a good balance between compression efficiency and coverage across different languages and domains.",
  },
  {
    q: "What are the goals of this project?",
    a: "The primary goal is deep understanding: to demystify language models by building every component from scratch. Secondary goals include creating a clean, readable reference implementation, experimenting with architectural variations, and sharing the learning journey with others who share the same curiosity about how these systems work.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section id="faq" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-2xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              FAQ
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium">
              Common questions about the project.
            </p>
          </div>
        </Reveal>

        <div className="space-y-0">
          {items.map((item, i) => (
            <motion.div
              key={item.q}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="border-2 border-[#F1F1F1]/10 bg-[#333333] -mt-0.5 first:mt-0 first:rounded-t last:rounded-b"
            >
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-[#F1F1F1]/[0.02] transition-colors duration-150 cursor-pointer"
              >
                <span className="text-sm font-bold text-[#F1F1F1] pr-4">{item.q}</span>
                <motion.div animate={{ rotate: open === i ? 180 : 0 }} transition={{ duration: 0.2 }}>
                  <ChevronDown className="w-4 h-4 text-[#FF5722] shrink-0" />
                </motion.div>
              </button>
              <AnimatePresence>
                {open === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <p className="px-6 pb-5 text-sm text-[#F1F1F1]/55 leading-relaxed font-medium border-t-2 border-[#F1F1F1]/5 pt-4">
                      {item.a}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
