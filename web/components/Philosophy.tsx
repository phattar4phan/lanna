import { motion } from "framer-motion";
import { Reveal } from "./utils";

const principles = [
  {
    title: "Curiosity",
    body: "Every curiousity started with a question: how does this actually work? What happens if we change it? How does this trash code work?",
  },
  {
    title: "Experimentation",
    body: "Ideas are created, tested, and broken overtime. Failure is just a part in the learning process.",
  },
  {
    title: "Engineering",
    body: "Code is written to be read, and understand easily. Not time for havily optimizing right now.",
  },
  {
    title: "Learning by Building",
    body: "Learn from the limitless creativities and failures, to understand it; you must build it.",
  },
  {
    title: "Simplicity",
    body: "Make it as understandable as it could be, not adding more complexity and larps.",
  },
];

export default function Philosophy() {
  return (
    <section id="philosophy" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-4xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              Philosophy
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium max-w-xl mx-auto">
              This project exists because building systems from scratch is one of the best ways to
              deeply understand them.
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {principles.map((p, i) => (
            <motion.div
              key={p.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="p-8 rounded border-2 border-[#F1F1F1]/10 bg-[#333333] hover:border-[#FF5722]/20 transition-colors duration-200"
            >
              <div className="w-8 h-1.5 bg-[#FFC107] mb-4" />
              <h3 className="text-lg font-bold text-[#F1F1F1] mb-3">{p.title}</h3>
              <p className="text-sm text-[#F1F1F1]/55 leading-relaxed font-medium">{p.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
