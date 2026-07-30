import { motion } from "framer-motion";
import { Reveal } from "./utils";

const steps = [
  {
    title: "Dataset Collection",
    body: "Collecting data from publicly available sources such as HuggingFaceFW/FineWeb-Edu and Allenai/Dolci-Instruct-SFT (huggingface.co)",
    tag: "Phase 1",
  },
  {
    title: "Cleaning & Processing",
    body: "Serialize the dataset into .txt files and remove unwanted data.",
    tag: "Phase 2",
  },
  {
    title: "Tokenizer Training",
    body: "Training a SentencePiece Unigram tokenizer on the dataset, balancing vocabulary size against compression efficiency.",
    tag: "Phase 3",
  },
  {
    title: "Model Training",
    body: "Training the transformer from random initialization, learning rate schedules, and F16 precision.",
    tag: "Phase 4",
  },
  {
    title: "Evaluation",
    body: "Measuring quality and performance, understanding what 50M parameters can and cannot do.",
    tag: "Phase 5",
  },
  {
    title: "Continuous Experiments",
    body: "Iterating on architecture, data, and training — each experiment reveals something new about how these models work.",
    tag: "Ongoing",
  },
];

export default function LearningJourney() {
  return (
    <section id="journey" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-3xl mx-auto">
        <Reveal>
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              Learning Journey
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium">
              From raw data to a working language model — every step documented.
            </p>
          </div>
        </Reveal>

        <div className="relative">
          <div className="absolute left-5 top-3 bottom-3 w-0.5 bg-[#F1F1F1]/15" />

          <div className="space-y-8">
            {steps.map((s, i) => (
              <motion.div
                key={s.title}
                initial={{ opacity: 0, x: -16 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
                className="relative pl-14"
              >
                <div className="absolute left-0 top-1 w-10 h-10 border-2 border-[#FF5722]/40 bg-[#2D2D2D] flex items-center justify-center">
                  <div className="w-3 h-3 bg-[#FF5722]" />
                </div>

                <div className="p-6 rounded border-2 border-[#F1F1F1]/10 bg-[#333333] hover:border-[#F1F1F1]/20 transition-colors duration-200">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-bold text-[#F1F1F1]">{s.title}</h3>
                    <span className="text-xs font-bold text-[#FFC107] bg-[#FFC107]/10 px-2.5 py-1 border border-[#FFC107]/20">
                      {s.tag}
                    </span>
                  </div>
                  <p className="text-sm text-[#F1F1F1]/55 leading-relaxed font-medium">{s.body}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
