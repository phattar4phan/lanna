import { motion } from "framer-motion";
import { Cpu, Layers, Route, Type, Zap, FlaskConical } from "lucide-react";
import { Reveal } from "./utils";

const cards = [
  {
    icon: Cpu,
    title: "Decoder-only Transformer",
    body: "Following the same design architect as models like LLaMAs, giving the almost-like pipeline with modern model training pipeline.",
  },
  {
    icon: Layers,
    title: "50M Parameters",
    body: "Small enough to train on low-end hardware, but can still be a meaningful masterpiece for individual.",
  },
  {
    icon: Route,
    title: "RoPE Positional Encoding",
    body: "Rotary Position Embedding encodes token positions with relative distance awareness, enabling better generalization to unseen sequence lengths.",
  },
  {
    icon: Type,
    title: "SentencePiece Tokenizer",
    body: "Unigram via SentencePiece handles subword tokenization, balancing vocabulary size with coverage across the language and domain.",
  },
  {
    icon: Zap,
    title: "Efficient Inference",
    body: "There's no efficiency inference yet as the model itself is not huge and is not for production.",
  },
  {
    icon: FlaskConical,
    title: "Experimental Training Pipeline",
    body: "Custom training loop with F16 precision, gradient accumulation, and learning rate schedule",
  },
];

export default function Architecture() {
  return (
    <section id="architecture" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-6xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              Architecture
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium max-w-xl mx-auto">
              Every component built from first principles — understanding how each piece fits
              together.
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((c, i) => (
            <motion.div
              key={c.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="group relative p-8 rounded border-2 border-[#F1F1F1]/10 bg-[#333333] hover:border-[#FF5722]/30 transition-colors duration-200"
            >
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#FF5722] opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              <div className="w-12 h-12 rounded border-2 border-[#F1F1F1]/10 flex items-center justify-center mb-5 group-hover:border-[#FF5722]/40 transition-colors duration-200">
                <c.icon className="w-6 h-6 text-[#FF5722]" />
              </div>
              <h3 className="text-lg font-bold text-[#F1F1F1] mb-3">{c.title}</h3>
              <p className="text-sm text-[#F1F1F1]/55 leading-relaxed font-medium">{c.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
