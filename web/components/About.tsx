import { Reveal } from "./utils";

export default function About() {
  return (
    <section id="about" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-3xl mx-auto">
        <Reveal>
          <div className="mb-16">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              About LLM
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mb-6" />
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="space-y-6 text-lg text-[#F1F1F1]/65 leading-relaxed font-medium">
            <p>
              LLM is a personal experimental language model — approximately 50 million parameters —
              built from the ground up to understand how modern language models actually work. It is
              not a commercial product. There is no pricing page, no enterprise plan, and no ambition
              to compete with production-scale systems.
            </p>
            <p>
              The project exists because the best way to understand something deeply is to build it
              yourself. Every component — from the tokenizer to the transformer blocks, from the
              attention mechanism to the training loop — is implemented with the goal of learning
              rather than optimizing for benchmarks.
            </p>
            <p>
              Along the way, LLM explores: transformer architectures (decoder-only design),
              tokenization strategies (SentencePiece BPE), positional encoding (RoPE), optimization
              algorithms (AdamW with weight decay), efficient inference techniques, scaling laws and
              their implications for small models, and model compression approaches like quantization
              and pruning.
            </p>
            <p>
              The codebase is written to be readable, educational, and approachable. If you are
              curious about how language models work under the hood, this project is for you.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
